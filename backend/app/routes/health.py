from fastapi import APIRouter

router = APIRouter()


@router.get("/", methods=["GET", "HEAD"])
def home():
    return {
        "project": "MandiCluster",
        "status": "running",
        "learning_type": "Unsupervised Learning",
    }
