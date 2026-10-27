from fastapi import APIRouter

router = APIRouter()


@router.api_route("/", methods=["GET", "HEAD"])
def home():
    return {
        "project": "MandiCluster",
        "status": "running",
        "learning_type": "Unsupervised Learning",
    }