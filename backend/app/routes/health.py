from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def home():
    return {
        "project": "MandiCluster",
        "status": "running",
        "learning_type": "Unsupervised Learning",
    }
