DATABASE_FILE = "test.db"
def download_database():
    s3.download_file(BUCKET_NAME, DATABASE_FILE, DATABASE_FILE)



def round_seconds(obj: dt.datetime) -> dt.datetime:
    if obj.microsecond >= 500_000:
        obj += dt.timedelta(seconds=1)
    return obj.replace(microsecond=0)


#DATA MODEL
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __repr__(self):
        return f"Comment('{self.body}', '{self.timestamp}')"
    def __str__(self):
        return f"{self.body} ------- {round_seconds(self.timestamp)}"
    

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='article', lazy=True)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


def get_all_comments():
    return [str(c) for c in  Comment.query.all() ]


class AddCommentForm(FlaskForm):
    body = StringField("Body", validators=[InputRequired()])
    submit = SubmitField("Post")



def get_number_comments():
    counts = len( Comment.query.all())
    return counts

def get_host_number():
    return get_number_comments()

##APP.PY
#@login_required
@app.route("/comments", methods=['GET', 'POST'])
def comment_handler():
    ALL_COMMENTS = get_all_comments()
    form = AddCommentForm()
    post_id  = get_number_comments()+1
     
    if request.method == 'POST': # this only gets executed when the form is submitted and not when the page loads
        if form.validate_on_submit():
            comment = Comment(body=form.body.data, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
            flash("Your comment has been added to the post", "success")        
            save_to_s3(DATABASE_FILE)
            
            return redirect(url_for("comment_handler",form=form, ALL_COMMENTS = ALL_COMMENTS))
        
    return render_template("comments.html", title="Comments", 
            form=form,ALL_COMMENTS=ALL_COMMENTS)
## COMMETS DB
##app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
##app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
#db = SQLAlchemy(app)


#download_database()
#db.create_all()
#SQL alchemy
#https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/



#ALL_COMMENTS = get_all_comments()
#print("ALL_COMMENTS: ", ALL_COMMENTS)

#simple_comments = 
'''
    <!doctype html>
    <title>Comments</title>
    <h1>Comments</h1>
'''