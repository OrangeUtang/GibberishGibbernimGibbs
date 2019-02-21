import unittest
import json
import io
import os
from ImgManager import app as tested_app
from ImgManager import db as tested_db
from ImgManager.config import TestConfig
from ImgManager.models import Person, Album, Picture

#tested_app.config.from_object(TestConfig)

class TestPerson(unittest.TestCase):
    def setUp(self):
        # set up the test DB
        self.db = tested_db
        self.db.create_all()

        self.app = tested_app.test_client()

        self.app.post("/register", data={"name": "Alice", "password": "Alice123"})
        self.app.post("/register", data={"name": "Bob", "password": "Bob123"})

        self.app.post("/login", data={"name": "Bob", "password": "Bob123"})
        self.app.post("/createAlbum", data={"name": "Album1"})
        self.app.post("/logout")
        picture_path = os.path.join(tested_app.root_path + '\pictures', 'test_img.jpg')
        picture_path2 = os.path.join(tested_app.root_path + '\pictures', 'test_img2.jpg')

        new_pic = Picture(name='tst_img', album_id=1, path=picture_path)
        new_pic2 = Picture(name='tst_img2', album_id=1, path=picture_path2)
        self.db.session.add(new_pic)
        self.db.session.add(new_pic2)
        self.db.session.commit()



    def tearDown(self):
        # clean up the DB after the tests
        Person.query.delete()
        Album.query.delete()
        Picture.query.delete()
        self.db.session.commit()

    def test_get_all_person(self):
        # send the request and check the response status code
        response = self.app.get("/person")
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        person_list = json.loads(str(response.data, "utf8"))
        self.assertEqual(type(person_list), list)
        self.assertDictEqual(person_list[0], {"id": "1", "name": "Alice"})
        self.assertDictEqual(person_list[1], {"id": "2", "name": "Bob"})

    def test_get_person_with_valid_id(self):
        # send the request and check the response status code
        response = self.app.get("/person/1")
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        person = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(person, {"id": "1", "name": "Alice"})

    def test_get_person_with_invalid_id(self):
        # send the request and check the response status code
        response = self.app.get("/person/1000000")
        self.assertEqual(response.status_code, 404)

        # convert the response data from json and call the asserts
        body = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(body, {"code": 404, "msg": "Cannot find this person id."})

    def test_register(self):
        # do we really need to check counts?
        initial_count = Person.query.count()

        # send a valid register request
        response = self.app.post("/register", data={"name": "bobby", "password": "bobby123"})
        self.assertEqual(response.status_code, 200)

        # send an invalid register request
        response = self.app.post("/register", data={"name": "bobby", "password": "bobby123"})
        self.assertEqual(response.status_code, 403)

        # assert db updated correctly
        # check if the DB was updated correctly
        updated_count = Person.query.count()
        self.assertEqual(updated_count, initial_count + 1)

    def test_login(self):
        # send an invalid login
        response = self.app.post("/login", data={"name": "Alce", "password": "Alice13"})
        self.assertEqual(response.status_code, 403)

        # send an invalid password
        response = self.app.post("/login", data={"name": "Alice", "password": "b"})
        self.assertEqual(response.status_code, 403)

        response = self.app.post("/login", data={"name": "Alice", "password": "Alice123"})
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        response = self.app.post("/login", data={"name": "Bob", "password": "Bob123"})
        self.assertEqual(response.status_code, 200)

        response = self.app.post("/logout")
        self.assertEqual(response.status_code, 200)

    def test_logout_notLogged(self):
        response = self.app.post("/logout")
        self.assertEqual(response.status_code, 302)

    def test_add_Album(self):
        response = self.app.post("/login", data={"name": "Bob", "password": "Bob123"})
        self.assertEqual(response.status_code, 200)

        init_alb_count = Album.query.count()

        response = self.app.post("/createAlbum", data={"name": "Summer"})
        self.assertEqual(response.status_code, 200)

        updated_count = Album.query.count()
        self.assertEqual(updated_count, init_alb_count + 1)

    def test_add_Album_invalid(self):
        response = self.app.post("/login", data={"name": "Alice", "password": "Alice123"})
        self.assertEqual(response.status_code, 200)

        init_alb_count = Album.query.count()

        # lacking data
        response = self.app.post("/createAlbum")
        self.assertEqual(response.status_code, 403)

        # should succeed
        response = self.app.post("/createAlbum", data={"name": "Summer"})
        self.assertEqual(response.status_code, 200)

        # should be invalid because same person has 2 album with same name
        response = self.app.post("/createAlbum", data={"name": "Summer"})
        self.assertEqual(response.status_code, 403)

        # should have only 1 added album
        updated_count = Album.query.count()
        self.assertEqual(updated_count, init_alb_count + 1)

    def test_display_all_album(self):
        response = self.app.post("/register", data={"name": "Paul", "password": "Paul123"})
        self.assertEqual(response.status_code, 200)

        response = self.app.post("/login", data={"name": "Paul", "password": "Paul123"})
        self.assertEqual(response.status_code, 200)

        response = self.app.post("/createAlbum", data={"name": "Album1"})
        self.assertEqual(response.status_code, 200)

        response = self.app.post("/createAlbum", data={"name": "Album2"})
        self.assertEqual(response.status_code, 200)

        response = self.app.get("/album")
        album_list = json.loads(str(response.data, "utf8"))
        self.assertEqual(album_list[0], {"id": "1", "name": "Album1", "person_id": "3"})
        self.assertEqual(album_list[1], {"id": "2", "name": "Album2", "person_id": "3"})

    def test_display_one_album(self):
        response = self.app.post("/register", data={"name": "testAlb", "password": "testAlb123"})
        self.assertEqual(response.status_code, 200)

        response = self.app.post("/login", data={"name": "testAlb", "password": "testAlb123"})
        self.assertEqual(response.status_code, 200)

        response = self.app.post("/createAlbum", data={"name": "Album3"})
        self.assertEqual(response.status_code, 200)

        response = self.app.get("/album/1")
        album = json.loads(str(response.data, "utf8"))
        self.assertEqual(album, {"id": "1", "name": "Album3", "person_id": "3"})

    def test_add_pic(self):
        init_pic_count = Picture.query.count()
        response = self.app.post("/register", data={"name": "PicTest", "password": "PicTest123"})
        self.assertEqual(response.status_code, 200)

        response = self.app.post("/login", data={"name": "PicTest", "password": "PicTest123"})
        self.assertEqual(response.status_code, 200)

        response = self.app.post("/createAlbum", data={"name": "Album2"})
        self.assertEqual(response.status_code, 200)

        with open('test_img.jpg', 'rb') as img1:
            # imgBytesIO = io.BytesIO(img1.read())

            try:
                # img = img1.read()
                imgBytesIO = io.BytesIO(img1.read())
            except:
                print("File can't be read.")

        response = self.app.post('/Album/2/addPicture', content_type='multipart/form-data',
                                 data={'image': (imgBytesIO, 'test_img.jpg'), 'name': 'testImg1'})

        self.assertEqual(response.status_code, 200)

        pic_count = Picture.query.count()
        self.assertEqual(init_pic_count+1, pic_count)

    def test_display_all_pic(self):
        response = self.app.get("/picture/1")
        picture_list = json.loads(str(response.data, "utf8"))
        self.assertEqual(picture_list[0], {"id": "1", "name": "test_img", "album_id": "1",
                                           "path": 'C:\\Users\\joedu\\Desktop\SOEN487_A1\\ImgManager\\pictures\\test_img.jpg'})

        self.assertEqual(picture_list[1], {"id": "2", "name": "test_img2", "album_id": "1",
                                           "path": 'C:\\Users\joedu\\Desktop\\SOEN487_A1\\ImgManager\\pictures\\test_img2.jpg'})

    def test_get_picture(self):
        # send the request and check the response status code
        response = self.app.get("/person/1")
        self.assertEqual(response.status_code, 200)

        # convert the response data from json and call the asserts
        picture = json.loads(str(response.data, "utf8"))
        self.assertDictEqual(picture, {"id": "1", "name": "test_img", "album_id": "1",
                                      "path": 'C:\\Users\\joedu\\Desktop\SOEN487_A1\\ImgManager\\pictures\\test_img.jpg'})

    def test_add_pic_OtherAlbum(self):
        response = self.app.post("/register", data={"name": "PicTest", "password": "PicTest123"})
        self.assertEqual(response.status_code, 200)

        response = self.app.post("/login", data={"name": "PicTest", "password": "PicTest123"})
        self.assertEqual(response.status_code, 200)

        response = self.app.post("/createAlbum", data={"name": "Album2"})
        self.assertEqual(response.status_code, 200)

        with open('test_img.jpg', 'rb') as img1:
            # imgBytesIO = io.BytesIO(img1.read())

            try:
                # img = img1.read()
                imgBytesIO = io.BytesIO(img1.read())
                print(imgBytesIO)
            except:
                print("File can't be read.")

        response = self.app.post('/Album/1/addPicture', content_type='multipart/form-data',
                                 data={'image': (imgBytesIO, 'test_img.jpg'), 'name': 'testImg1'})

        self.assertEqual(response.status_code, 403)

