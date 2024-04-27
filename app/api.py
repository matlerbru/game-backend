#!/usr/bin/python3
import auth.router
import user.router
from fastapi import FastAPI
import di

api = FastAPI(root_path=di.container.config.root_path())

api.include_router(auth.router.router, prefix="/auth")
api.include_router(user.router.router, prefix="/user")


@api.get("/")
def root():
    return str(di.container.config.root_path())
