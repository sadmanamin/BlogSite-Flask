from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///test.db'
db = SQLAlchemy(app)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200),nullable=False)
    email = db.Column(db.String(200),nullable=False)
    password = db.Column(db.String(200),nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    blogs = db.relationship('Blog',backref='owner')

    def __repr__(self):
        return '<User %r' % self.id

class Blog(db.Model):
    bid = db.Column(db.Integer, primary_key=True)
    blog_name = db.Column(db.String(200),nullable=False)
    blog_content = db.Column(db.String(5000),nullable=False)
    blog_category = db.Column(db.String(20),nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_name = db.Column(db.Integer, db.ForeignKey('user.name'),
        nullable=False)

    def __repr__(self):
        return '<Blog %r' % self.bid




@app.route('/')
@app.route('/index')
def index():
    blogs = Blog.query.order_by(Blog.date_created).all()
    return render_template('index.html',blogs=blogs,logged=False)



@app.route('/home/<int:id>')
def home(id):
    user = User.query.get_or_404(id)
    blogs = Blog.query.order_by(Blog.date_created).all()
    return render_template('index.html',blogs=blogs,user=user,logged=True)



@app.route('/myblog/<int:id>',methods=['POST','GET'])
def blogs(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        blog_name,blog_content,blog_category = request.form['cBlogname'],request.form['cBlogcontent'],request.form['cCategory']
        
        if len(blog_name)==0 or len(blog_content)==0 or len(blog_category)==0:
            return render_template('error_page.html',msg="Field cannot be empty")

        blog = Blog(blog_name=blog_name,blog_content=blog_content,blog_category=blog_category,owner=user)
        try:
            user.blogs.append(blog)
            db.session.add(user)
            db.session.commit()
            blogs = Blog.query.filter_by(user_name=user.name).all()
            print(len(blogs))
            return render_template('single-standard.html',blogs=blogs,user=user,logged=True)
        except:
            return render_template('error_page.html',msg="Problem In creating blog")

    else:
        blogs = Blog.query.filter_by(user_name=user.name).all()
        return render_template('single-standard.html',blogs=blogs,user=user,logged=True)



@app.route('/blog_update/<int:id1>/<int:id2>',methods=['POST','GET'])
def updateBlog(id1,id2):
    user = User.query.get_or_404(id1)
    blog = Blog.query.get_or_404(id2)
    if request.method == 'POST':
        blog.blog_name = request.form['cBlogname']
        blog.blog_content = request.form['cBlogcontent']
        blog.blog_category = request.form['cCategory']
        db.session.commit()
        blogs = Blog.query.filter_by(user_name=user.name).all()
        return redirect('/myblog/'+str(id1))
    else:
        #blogs = Blog.query.filter_by(user_name=user.name).all()
        return render_template('update_blog.html',blog=blog,user=user,logged=True)



@app.route('/delete_blog/<int:id1>/<int:id2>')
def deleteBlog(id1,id2):
    user = User.query.get_or_404(id1)
    try:
        Blog.query.filter_by(bid=id2).delete()
        db.session.commit() 
        return redirect('/myblog/'+str(id1))
    except:
        return render_template('error_page.html',msg='Error in Deleting')



@app.route('/signup',methods=['POST','GET'])
def signup():

    if request.method == 'POST':

        name,email,pass1,pass2 = request.form['cName'],request.form['cEmail'],request.form['cPass1'],request.form['cPass2']
        
        if len(name)==0 or len(email)==0 or len(pass1)==0 or len(pass2)==0:
            return render_template('error_page.html',msg="Field cannot be empty")

        elif pass1!=pass2:
            return render_template('error_page.html',msg='Password did not match')

        else:
            new_user = User(name=name,email=email,password=pass1)
            try:
                db.session.add(new_user)
                db.session.commit()
                user = User.query.order_by(User.date_created.desc()).first()
                return redirect('/home/'+str(new_user.id))
            except:
                return render_template('error_page.html',msg='Error in creating user')


    else:
        return render_template('signup.html')

        

@app.route('/login',methods=['POST','GET'])
def login():

    if request.method == 'POST':

        email,password = request.form['cEmail'],request.form['cPass']

        if len(email)==0 or len(password)==0:
            return render_template('error_page.html',msg="Field cannot be empty")

        user = User.query.filter_by(email=email).first()

        if user.email == email and user.password==password:
            return redirect('/home/'+str(user.id))
        else:
            return render_template('error_page.html',msg='No User found')


    else:
        return render_template('login.html')




if __name__ == '__main__':
    app.run(debug=True)