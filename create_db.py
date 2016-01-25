from app import db, Register, User

db.drop_all()
db.create_all()


# test Register
reg = Register('18601618863', '100086', False)
user = User('18601618863', 'hello')
db.session.add(reg)
db.session.add(user)
db.session.commit()
