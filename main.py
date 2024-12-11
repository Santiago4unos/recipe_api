#Python
import json

#Pydantic
from pydantic import (
    BaseModel, HttpUrl, Field
    )

#FastAPI
from fastapi import (
    FastAPI, Body, 
    status, HTTPException
    )
import uvicorn

app = FastAPI()

def get_recipes(filename) -> None: 
    with open(f"{filename}.json", "r", encoding="utf-8") as f:
        recipes = json.load(f)
        return recipes


def write_json(filename: str, recipe: dict) -> dict:
    with open(f"{filename}.json", "r+", encoding="utf-8") as f:
        recipes: list[dict] = json.load(f)
        recipe["id"] = len(recipes) + 1
        recipe["image_link"] = str(recipe["image_link"])
        recipes.append(recipe)
        f.seek(0)
        f.write(json.dumps(recipes, indent=4, ensure_ascii=False))
        f.truncate()
        return recipe


def delete_from_json(filename: str, id: int) -> dict:
    with open(f"{filename}.json", "r+", encoding="utf-8") as f:
        recipes: list[dict] = json.load(f)
        for idx, recipe in enumerate(recipes):
            if recipe["id"] == id:
                recipes.pop(idx)
                f.seek(0)
                f.write(json.dumps(recipes))
                f.truncate()
                return recipe
        raise HTTPException(status_code=404, detail="Recipe not found")


class Recipe(BaseModel):
    id: int = Field(...)
    name: str = Field(
    ...,
    min_length=1,
    max_length=50,
    example="Spaghetti"
    )
    author: str = Field(
    ...,
    min_length=1,
    max_length=50,
    example="John Doe"
    )
    image_link: HttpUrl = Field(...)
    recipe: list[str] = Field(...)


@app.get(
    path="/",
    status_code=status.HTTP_200_OK,
    tags=["Home"]
    )
def home():
    return {"Hello": "World"}

@app.get(
    path="/recipe/all",
    status_code=status.HTTP_200_OK,
    response_model=list[Recipe],
    tags=["Recipes"]
)
def get_all_recipes():
    """
    Get all recipes in the database.

    Returns:
        list[Recipe]: An object containing the list of recipes.
    """
    return get_recipes("recipes")
@app.get(
    path="/recipe/{id}",
    status_code=status.HTTP_200_OK,
    response_model=Recipe,
    tags=["Recipes"]
)
def get_recipe(id: int):
    """
    Get a recipe by its id

    This path operation gets a recipe by its id

    Parameters:
    - Path parameter:
        - **id: int** -> The id of the recipe to be retrieved

    Returns a Recipe model with the recipe information
    """
    recipes = get_recipes("recipes")
    for recipe in recipes:
        if recipe["id"] == id:
            return recipe
    raise HTTPException(status_code=404, detail="Recipe not found")

@app.post(
    path="/recipe/new",
    response_model=Recipe,
    status_code=status.HTTP_201_CREATED,
    tags=["Recipes"],
    summary="Creates a recipe in the app"
    )

def create_recipe(recipe: Recipe = Body(...)):
    """
    Create Recipe

    This path operation creates a recipe in the app and saves the information in the database

    Parameters:
    - Request body parameter:
        - **recipe: Recipe** -> A recipe model with id, title, author, image link and instructions

    Returns a recipe model with id, title, author, image link and instructions
    """
    return write_json("recipes", recipe.model_dump())

@app.delete(
    "/recipe/{id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Recipes"]
    )
def delete_recipe(id: int):    
    """
    Delete a recipe by its id

    This path operation deletes a recipe

    Parameters:
    - Path parameter:
        - **id: str** -> The id of the recipe to be deleted

    Returns a 204 status code when the recipe is deleted
    """
    return delete_from_json("recipes", id)

# Favorites
@app.get(
    "/recipe/favorites/all",
    status_code=status.HTTP_200_OK,
    tags=["Recipes", "Favorites"]
)
def get_all_favorite_recipes():
    return get_all_recipes("favorite_recipes")


@app.post(
    "/recipe/favorites/new",
    status_code=status.HTTP_201_CREATED,
    tags=["Recipes", "Favorites"]
)
def post_favorite_recipe(recipe: Recipe = Body(...)):
    """
    Post a favorite recipe

    This path operation adds a recipe to the favorites

    Parameters:
    - Request body parameter:
        - **recipe: Recipe** -> A recipe model with id, title, author, image link and instructions

    Returns the recipe added
    """
    return write_json("favorite_recipes", recipe.model_dump())


@app.delete(
    "/recipe/favorites/delete/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Recipes", "Favorites"]
)
def delete_favorite_recipe(id: int):
    """
    Delete a favorite recipe by its id

    This path operation deletes a favorite recipe

    Parameters:
    - Path parameter:
        - **id: int** -> The id of the recipe to be deleted

    Returns a 204 status code when the recipe is deleted
    """
    return delete_from_json("favorite_recipes", int(id))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)