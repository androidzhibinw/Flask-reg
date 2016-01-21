from app import db, Register

db.drop_all()
db.create_all()


# test Register
reg = Register('18601618863', '100086', False)
db.session.add(reg)
db.session.commit()
