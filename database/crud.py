# from sqlalchemy.orm import Session
# from . import models, schemas


# def get_user(db: Session, user_id: int):
#     return db.query(models.User).filter(models.User.id == user_id).first()


# def get_user_by_username(db: Session, username: str):
#     return db.query(models.User).filter(models.User.username == username).first()


# def get_users(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.User).offset(skip).limit(limit).all()


# def create_user(db: Session, user: schemas.UserCreate):
#     db_user = models.User(
#         name=user.name, password=user.password, username=user.username
#     )  # can use dict to compact code
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user


# def get_collections(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Collection).offset(skip).limit(limit).all()


# def get_collections_by_id_user(
#     db: Session, skip: int = 0, limit: int = 100, id_user: int = 0
# ):
#     return (
#         db.query(models.Collection)
#         .filter(models.Collection.user_id == id_user)
#         .offset(skip)
#         .limit(limit)
#         .all()
#     )


# def add_collection(db: Session, collection: schemas.CollectionCreate, user_id: int):
#     db_collection = models.Collection(
#         name=collection.name, user_id=user_id
#     )  # can use dict to compact code
#     db.add(db_collection)
#     db.commit()
#     db.refresh(db_collection)
#     return db_collection


# def add_image(db: Session, image: schemas.ImageCreate):
#     db_image = models.Image(
#         name=image.name, note_id=image.note_id, path_file=image.path_file
#     )
#     db.add(db_image)
#     db.commit()
#     db.refresh(db_image)
#     return db_image


# def delete_image(db: Session, id_image: int):
#     db_image = db.query(models.Image).filter(models.Image.id == id_image).first()
#     db.delete(db_image)
#     db.commit()
#     return db_image


# def create_user_collection(db: Session, item: schemas.CollectionCreate, user_id: int):
#     db_item = models.Item(**item.dict(), user_id=user_id)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item


# def add_note(db: Session, note: schemas.NoteCreate):
#     db_note = models.Note(
#         name=note.name,
#         text_content=note.text_content,
#         collection_id=note.collection_id,
#     )  # can use dict to compact code
#     db.add(db_note)
#     db.commit()
#     db.refresh(db_note)
#     return db_note


# def update_note(db: Session, note: schemas.Note):
#     db_note = db.query(models.Note).filter(models.Note.id == note.id).first()
#     db_note.name = note.name
#     db_note.text_content = note.text_content
#     db.commit()
#     db.refresh(db_note)
#     return db_note


# def update_collection(db: Session, collection: schemas.Collection):
#     db_collection = (
#         db.query(models.Collection)
#         .filter(models.Collection.id == collection.id)
#         .first()
#     )
#     db_collection.name = collection.name
#     db.commit()
#     db.refresh(db_collection)
#     return db_collection


# def get_image_by_id(db: Session, id_image: int):
#     return db.query(models.Image).filter(models.Image.id == id_image).first()


# def get_notes_by_id_collection(
#     db: Session, skip: int = 0, limit: int = 100, id_collection: int = 0
# ):
#     return (
#         db.query(models.Note)
#         .filter(models.Note.collection_id == id_collection)
#         .offset(skip)
#         .limit(limit)
#         .all()
#     )


# def delete_note_by_id(db: Session, id_note: int):
#     db.query(models.Note).filter(models.Note.id == id_note).delete()
#     db.commit()
#     return True


# def delete_collection_by_id(db: Session, id_collection: int):
#     db.query(models.Collection).filter(models.Collection.id == id_collection).delete()
#     db.commit()
#     return True
