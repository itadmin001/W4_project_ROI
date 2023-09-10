from flask import Flask, render_template, url_for,redirect,flash,request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import delete,select,update,and_,Column, String, Integer,DateTime,ForeignKey,Text,text,Numeric
from sqlalchemy.orm import relationship,backref
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_login import LoginManager,UserMixin,login_required,login_user,logout_user,current_user
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,DecimalField,HiddenField
from wtforms.validators import InputRequired,Email,Length
import locale
from helper import get_image,calc_roi
from flask_migrate import Migrate

locale.setlocale(locale.LC_ALL,'')
locale.currency(12345.67, grouping=True)

roi = Flask(__name__)

roi.config['SECRET_KEY'] = 'superKalfragilistic'
login_manager=LoginManager()
login_manager.login_view = "login"
login_manager.init_app(roi)
bcrypt = Bcrypt(roi)

roi.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://hbfbkyvp:iMgXa9wFPwNZCbuzOd8A9kITRc_522Cg@isilo.db.elephantsql.com/hbfbkyvp'
db=SQLAlchemy(roi)
# db.init_app(roi)
migrate = Migrate(roi, db)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

class Users(db.Model,UserMixin):
    __tablename__ = "users"
    user_id =           Column("user_id", Integer,primary_key=True,autoincrement=True)
    first_name =        Column("fname",Text,default="none")
    last_name =         Column("lname",Text,default="none")
    email =             Column("email",Text,unique=True,nullable=False)
    phone =             Column("phone",Text,default="none")
    username =          Column("username",Text,unique=True,nullable=False)
    password =          Column("pwd",Text,nullable=False)
    created_on =        Column("created_on", DateTime(timezone=True),default=datetime.now())
    property =          relationship('Property', backref='users',cascade='all,delete',passive_deletes=True)

    def __init__(self, email, password,username):
        self.first_name = ""
        self.last_name = ""
        self.email = email
        self.phone = ""
        self.password = password
        self.username = username

    def pass_hash(password):
        hash_pwd = bcrypt.generate_password_hash(password)
        return hash_pwd.decode('utf-8')
    
    def get_id(self):
        return self.user_id

    def __repr__(self):
        return f"<USER ID: {self.user_id}>"
    
class Income(db.Model):
    __tablename__ =         "income"
    inc_id =                Column("inc_id",Integer, primary_key=True,autoincrement=True)
    prop_id =               Column("prop_id",Integer,ForeignKey('property.prop_id',ondelete='cascade'))
    name =                  Column("name",Text,default = "")
    amount =                Column("amount",Numeric(10,2),default=0)
    user_id =               Column(Integer,ForeignKey('users.user_id'))

    def __init__(self, prop_id, name,amount,user_id):
        self.prop_id = prop_id
        self.name = name
        self.amount = amount
        self.user_id = user_id

    def __repr__(self):
        return f"<INCOME: {self.name} AMOUNT: {self.amount}>"
    
class Expenses(db.Model):
    __tablename__ =         "expense"
    exp_id =                Column("inc_id",Integer, primary_key=True,autoincrement=True)
    prop_id =               Column("prop_id",Integer,ForeignKey('property.prop_id',ondelete='cascade'))
    name =                  Column("name",Text,default='none')
    amount =                Column("amount",Numeric(10,2),default=0)
    user_id =               Column(Integer,ForeignKey('users.user_id'))

    def __init__(self,prop_id,name,amount,user_id):
        self.prop_id = prop_id
        self.name =  name
        self.amount = amount
        self.user_id = user_id

    def __repr__(self):
        return f"<EXPENSE: {self.name} AMOUNT: {self.amount}>"

class Property(db.Model):
    __tablename__ =         "property"
    prop_id =               Column(Integer, primary_key=True,autoincrement=True)
    address =               Column(Text,nullable=False)
    purch_price =           Column(Numeric(10,2),nullable=False)
    est_rent =              Column(Numeric(10,2),nullable=False)
    _user_id =              Column(Integer,ForeignKey('users.user_id',ondelete='cascade'))
    image =                 Column(String, nullable=False)
    roi =                   Column(Numeric(5,2))
    income =                relationship('Income', backref='property', cascade='all,delete',passive_deletes=True)
    expenses =              relationship('Expenses', backref='property', cascade='all,delete',passive_deletes=True)
    
    def __init__(self,address,purch_price,est_rent,_user_id,image=""):
        self.address = address
        self.purch_price = purch_price
        self.est_rent = est_rent
        self._user_id = _user_id
        self.image = self.set_image(image,address)

    def set_image(self,image,address):
        if not image:
            image=get_image(address)
        return image
    
    def __repr__(self):
        return f"<ADDRESS: {self.address}>"

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(),Length(min=4,max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8,max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    username =  StringField('username', validators=[InputRequired(),Length(min=4,max=15)])
    password =  PasswordField('password', validators=[InputRequired(), Length(min=8,max=80)])
    email =     StringField('email',validators=[InputRequired(),Email(message='Invalid email'),Length(max=100)])

class AddPropertyForm(FlaskForm):
    address =       StringField('Address', validators=[InputRequired(),Length(max=100)])
    purch_price =   DecimalField('Purchase Price',validators=[InputRequired()])
    est_rent =      DecimalField('Estimated Rent',validators=[InputRequired()])
    image =         StringField("Image URL **Optional")

class AddImageForm(FlaskForm):
    imageURL = StringField("Image URL")

class IncomeForm(FlaskForm):
    income_amt =        DecimalField("Income Amount")
    income_name =       StringField("Income Name")
    property_id =       HiddenField(Integer)

class ExpenseForm(FlaskForm):
    expense_amt =       DecimalField("Expense Amount")
    expense_name =      StringField("Expense Name")
    property_id =       HiddenField(Integer)

@roi.route('/', methods = ['POST','GET'])
def index():
    return render_template('index.html')

@roi.route('/account', methods = ['POST','GET'])
@login_required
def account():
    return render_template('my_account.html')

@roi.route('/properties', methods = ['POST','GET'])
@login_required
def properties():
   
    prop_data= db.session.execute(text(f'SELECT * FROM property WHERE _user_id = {current_user.user_id}'))
    prop_count = len(prop_data.all())
    if prop_count < 1:
        return render_template('my_properties.html', no_properties=True)
    
    prop_data= db.session.execute(text(f'SELECT * FROM property WHERE _user_id = {current_user.user_id}'))
    properties = prop_data.all()
    return render_template('my_properties.html',properties=properties)

@roi.route('/Add-Image/<prop_id>',methods=['GET','POST'])
@login_required
def add_image(prop_id):
    form=AddImageForm()
    if form.validate_on_submit():
        img_url = form.imageURL.data
        #### This looks like the safer and more acceptable way to add/update ####
        
        query = text('UPDATE property SET image = :img_url WHERE property.prop_id = :prop_id AND property._user_id = :user_id')
        db.session.execute(query, {"img_url": img_url, "prop_id": prop_id, "_user_id": current_user.user_id})
        db.session.commit()
        return redirect('/properties')
    
    return render_template('add_image.html',form=form,prop_id=prop_id)

@roi.route('/add-edit',methods=['POST','GET'])
@login_required
def add_edit():
    form = AddPropertyForm()  
    if form.validate_on_submit():
        address = form.address.data
        purchase = form.purch_price.data
        est_rent = form.est_rent.data
        purchase_price = form.purch_price.data
        new_property=Property(address=address,purch_price=purchase,est_rent=est_rent,_user_id=current_user.user_id)
        db.session.add(new_property)
        db.session.commit()
        prop_id_q = db.session.execute(select(Property.prop_id).where(Property.address == address))
        prop_id = prop_id_q.all()[0][0]
        expense_amount = purchase_price
        expense_name = "Purchase Price"
        new_expense=Expenses(name=expense_name,amount=expense_amount,prop_id=prop_id,user_id=current_user.user_id)
        db.session.add(new_expense)
        db.session.commit()
        return redirect(url_for('properties'))
    
    return render_template('add_edit_property.html',form=form)

@roi.route('/delete/<id>', methods=['POST','GET'])
@login_required
def prop_delete(id):
    db.session.execute(delete(Property).where(Property.prop_id == id))
    db.session.commit()
    return redirect('/properties')

@roi.route('/view-exp-inc',defaults={'id':0}, methods = ['POST','GET'])
@roi.route('/view-exp-inc/<id>', methods = ['POST','GET'])
@login_required

def view_exp_inc(id):
    prop_data=db.session.execute(select(Property).join(Users).filter(Users.user_id==current_user.user_id).filter(Property.prop_id==id))
    property = [data[0] for data in prop_data]
    income_data = db.session.execute(select(Income).join(Property).filter(Income.prop_id == id))
    expense_data = db.session.execute(select(Expenses).join(Property).filter(Expenses.prop_id == id))
    incomes=(income_data.freeze().data)
    expenses=(expense_data.freeze().data)
    if len(incomes) < 1 and len(expenses) < 1:
        no_monies=True
        return render_template('inc_exp_view.html', no_monies=no_monies,property=property,id=id)
    else:
        income_sum=0
        for income in incomes:
            income_sum+=income.amount      
        expense_sum=0
        for expense in expenses:
            expense_sum+=expense.amount

        return render_template('inc_exp_view.html',incomes=incomes,expenses=expenses,property=property,expense_sum=expense_sum,income_sum=income_sum)

@roi.route('/Income',defaults={'id':0},methods=['POST','GET'])
@roi.route('/Income/<id>',methods=['POST','GET'])
@login_required
def add_inc(id):
    prop = db.session.execute(select(Property).where(Property.prop_id==id))
    props=list(map(list, prop))
    address = props[0][0].address
    form = IncomeForm()
    if request.method=="POST" and form.validate_on_submit():
        prop_id = id
        income_amount = form.income_amt.data
        income_name = form.income_name.data

        new_income=Income(name=income_name,amount=income_amount,prop_id=id,user_id=current_user.user_id)
        db.session.add(new_income)
        db.session.commit()

        exp_total = db.session.execute(text(f'select sum(amount) from expense inner join property on property.prop_id = expense.prop_id where expense.user_id = {current_user.user_id}'))
        inc_total = db.session.execute(text(f'select sum(amount) from income inner join property on property.prop_id = income.prop_id where income.user_id = {current_user.user_id}'))
        roi= calc_roi(props[0][0].purch_price,exp_total.all()[0][0],inc_total.all()[0][0])
        roif = "%.2f" % roi
        query=text(f'UPDATE property SET roi = {roif} WHERE property.prop_id = {prop_id}')
        db.session.execute(query)
        db.session.commit()
        return redirect('/properties')
    
    return render_template('add_income.html',form=form,id=id,address=address)

@roi.route('/Expense',defaults={'id':0},methods=['POST','GET'])
@roi.route('/Expense/<id>',methods=['POST','GET'])
@login_required
def add_exp(id):
    prop = db.session.execute(select(Property).where(Property.prop_id==id))
    address = prop.freeze().data[0].address
    form = ExpenseForm()
    if request.method=="POST" and form.validate_on_submit():
        prop_id = id
        expense_amount = form.expense_amt.data
        expense_name = form.expense_name.data
        new_expense=Expenses(name=expense_name,amount=expense_amount,prop_id=id,user_id=current_user.user_id)
        db.session.add(new_expense)
        db.session.commit()
        return redirect('/properties')
    
    return render_template('add_expense.html',form=form,id=id,address=address)
    
@roi.route('/contact', methods = ['POST','GET'])
def contact():
    return render_template('contact.html')

@roi.route('/login', methods = ['POST','GET'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        user_data = db.session.execute(select(Users).where(Users.username == form.username.data))
        user = (user_data.freeze().data)
        if len(user) < 1:
            flash("Username not found")
            # render_template('login.html',form=form)
        else:
            if form.validate_on_submit():
                password = form.password.data
                pwd = user[0].password
            
                if user != None:
                    if bcrypt.check_password_hash(pwd, password) == True:
                        user[0].authenticated = True
                        db.session.add(user[0])
                        db.session.commit()
                        login_user(user[0], remember=True)
                        flash('Logged in successfully.')
                        next = request.args.get('next')
                        return redirect(next or url_for('account'))
                    else: 
                        flash('Incorrect Password')
                        return render_template("login.html",form=form)
                else: 
                    flash("User not found")
                    return render_template("login.html",form=form)   
                  
    return render_template("login.html",form=form)

@roi.route("/logout", methods=['GET','POST'])
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    flash("Logged out successfully")
    return redirect("/login")

@roi.route('/register', methods = ['POST','GET'])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        usrname = form.username.data
        eml = form.email.data
        username_check = (db.session.execute(select(Users).where(Users.username==usrname))).freeze().data
        email_check = (db.session.execute(select(Users).where(eml==Users.email))).freeze().data
        if len(email_check) > 0:
            flash('This email address is already in use', category='error')
        elif len(username_check) > 0:
            flash('This username is already in use, please try again', category='error')
        else:
            hpwd = Users.pass_hash(form.password.data)
            new_user = Users(username=usrname,email=eml,password=hpwd)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))

    return render_template('register.html',form=form)

with roi.app_context():
    db.create_all()

if __name__ == '__main__':
    roi.run(debug=True)