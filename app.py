import database_utils
from content import *
from flask import *
from user_profile import *
import random
import bcrypt
import flask.sessions
import json
import time
import Levenshtein

SPELLCHECK_LIMIT = 5

app = Flask(__name__)

app.secret_key = bcrypt.hashpw(uuid.uuid1().hex.encode("UTF-8"), bcrypt.gensalt()).decode("UTF-8")


def get_user_profile_from_database(username, password):
    if "@" in username:
        rows = database_utils.get_all_with_constraint("databases/users.db", "users",
                                                      modifier=database_utils.CombinationModifier.And, email=username)
    else:
        rows = database_utils.get_all_with_constraint("databases/users.db", "users",
                                                      modifier=database_utils.CombinationModifier.And,
                                                      username=username)

    if len(rows) > 0:
        for row in rows:
            if bcrypt.checkpw(password.encode('UTF-8'), row['Password'].encode('UTF-8')):
                profile = UserProfile(row['Username'], row['Email'], row['FirstName'], row['LastName'], row['Avatar'],
                                      row['Public'], row['Id'], row['CanPublish'])
                return profile
            else:
                return "Incorrect Password"
    else:
        return "Username Not Found"


def does_user_exist_in_database(username):
    if "@" in username:
        rows = database_utils.get_all_with_constraint("databases/users.db", "users",
                                                      modifier=database_utils.CombinationModifier.And, email=username)
    else:
        rows = database_utils.get_all_with_constraint("databases/users.db", "users",
                                                      modifier=database_utils.CombinationModifier.And,
                                                      username=username)
    return len(rows)


def add_new_user_to_database(profile, password):
    hashed = bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt()).decode('UTF-8')
    database_utils.insert("databases/users.db", "users", username=profile.username, email=profile.email,
                          password=hashed, firstname=profile.first_name, lastname=profile.last_name,
                          avatar=profile.avatar, id=profile.id, public="0", canpublish="0")


def get_videos_owned_by_user(user):
    vids = []
    rows = database_utils.get_all_with_constraint("databases/repository.db", "video", ownerid=user.id)
    for row in rows:
        vids.append(
            Video(row["name"], row["location"], row["thumbnail"], row["date"], row["id"], row["views"],
                  row['description'], row["public"]))
    return vids


def does_user_own_video(user, video_id):
    rows = database_utils.get_all_with_constraint("databases/repository.db", "video", ownerid=user.id, id=video_id)
    return len(rows) > 0


def get_list_of_videos():
    ls = []
    # rows = database_utils.get_all("databases/repository.db", "Video")
    rows = database_utils.get_all_with_constraint("databases/repository.db", "Video",
                                                  modifier=database_utils.CombinationModifier.And, Public=1)
    for row in rows:
        ls.append(
            Video(row['name'], row['location'], row['thumbnail'], row['date'], row['id'], row['views'],
                  row['description'], row['public']))

    return ls


def get_list_of_audio():
    ls = []
    # rows = database_utils.get_all("databases/repository.db", "Audio")
    rows = database_utils.get_all_with_constraint("databases/repository.db", "Audio",
                                                  modifier=database_utils.CombinationModifier.And, Public=1)
    for row in rows:
        ls.append(Audio(row['name'], row['location'], row['date'], row['id'], row['views'], row['public']))

    return ls


def search_list_video(query):
    # rows = database_utils.execute_read("databases/repository.db",
    #                                    "SELECT * FROM Video WHERE Name LIKE '%" + query + "%' AND Public=1")
    # ls = []
    # for row in rows:
    #     ls.append(Video(row['name'], row['location'], row['date'], row['id'], row['public']))
    # return ls
    rows = []
    queries = query.lower().split(" ")
    for vid in get_list_of_videos():
        for q in queries:
            if Levenshtein.distance(vid.name.lower(), q) <= SPELLCHECK_LIMIT:
                rows.append(vid)
                break
    return rows


def search_list_audio(query):
    rows = database_utils.execute_read("databases/repository.db",
                                       "SELECT * FROM Audio WHERE Name LIKE '%" + query + "%' AND Public=1")
    ls = []
    for row in rows:
        ls.append(Audio(row['name'], row['location'], row['date'], row['id'], row['public']))
    return ls


def get_video_by_id(id):
    rows = database_utils.get_all_with_constraint("databases/repository.db", "Video",
                                                  modifier=database_utils.CombinationModifier.And, Id=id)
    ls = []
    for row in rows:
        ls.append(
            Video(row['name'], row['location'], row['thumbnail'], row['date'], row['id'], row['views'],
                  row['description'], row['public']))

    if len(ls) > 1:
        if not ls[0].public:
            return "private"
        print("ERROR: More than one video was found with id of " + str(id) + "\n Will return the first one")
        return ls[0]
    elif len(ls) == 1:
        return ls[0]
    return None


def get_audio_by_id(id):
    rows = database_utils.get_all_with_constraint("databases/repository.db", "Audio",
                                                  modifier=database_utils.CombinationModifier.And, Id=id)
    ls = []
    for row in rows:
        aud = Audio(row['name'], row['location'], row['date'], row['id'], row['public'])
        ls.append(aud)
    if len(ls) > 1:
        if not ls[0].public:
            return "private"
        print("ERROR: More than one audio was found with id of " + str(id) + "\n Will return the first one")
        return ls[0]
    elif len(ls) == 1:
        return ls[0]
    return None


@app.route('/')
@app.route('/home')
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        form_data = request.form
        profile_result = get_user_profile_from_database(form_data['loginUsername'], form_data['loginPassword'])

        if type(profile_result) == UserProfile:
            print("Logging in successfully " + str(profile_result))
            session['LoggedUser'] = profile_result.json()
            return redirect(url_for("user"))

        else:
            if profile_result == "Username Not Found":
                return render_template("error.html",
                                       fun_text="You don't exist!!!\nWe could not find your username in our systems",
                                       technical_text="Database query returned NULL")
            elif profile_result == "Incorrect Password":
                return render_template("error.html",
                                       fun_text="Sorry, the password you entered is incorrect\nPlease try again!",
                                       technical_text="Password hashes don't match")
    else:
        return render_template("login.html")


@app.route("/logout", methods=['GET'])
def logout():
    session.pop('LoggedUser', None)
    return redirect(url_for("home"))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        form_data = request.form
        if does_user_exist_in_database(form_data['registerUsername']) == 0:
            profile = UserProfile(form_data['registerUsername'], form_data['registerEmail'],
                                  form_data['registerFirstName'], form_data['registerLastName'], None, False,
                                  generate_new_user_id(), False)
            add_new_user_to_database(profile, form_data['registerPassword'])
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/user")
def user():
    if 'LoggedUser' in session.keys() and session['LoggedUser'] is not None:
        user_json = json.loads(session['LoggedUser'])
        profile = UserProfile(user_json['username'], user_json['email'],
                              user_json['first_name'],
                              user_json['last_name'], user_json['avatar'],
                              user_json['public'], user_json['id'], user_json['can_publish'])
        vids = get_videos_owned_by_user(profile)

        return render_template("userProfile.html",
                               profile=profile, videos=vids)
    else:
        return redirect(url_for("login"))


@app.route("/edit", methods=['GET', 'POST'])
def edit():
    if 'id' not in request.args:
        return access_denied(404)

    video_id = request.args["id"]

    if 'LoggedUser' in session.keys() and session['LoggedUser'] is not None:
        user_json = json.loads(session['LoggedUser'])
        profile = UserProfile(user_json['username'], user_json['email'],
                              user_json['first_name'],
                              user_json['last_name'], user_json['avatar'],
                              user_json['public'], user_json['id'], user_json['can_publish'])
        if does_user_own_video(profile, video_id):
            vid = get_video_by_id(video_id)
            if request.method == 'GET':
                return render_template("edit.html", video=vid)
            else:

                return render_template("edit.html", video=vid, status="saved")
        else:
            return access_denied(403)
    else:
        return redirect(url_for("login"))


@app.route("/content", methods=['GET'])
def content():
    if 'search' in request.args:
        return render_template("content.html", videos=search_list_video(request.args['search']),
                               search=request.args['search'])

    videos = get_list_of_videos()
    return render_template("content.html", videos=videos)


@app.route("/watch", methods=['GET'])
def watch():
    if 'id' in request.args:
        vid = get_video_by_id(request.args['id'])
        if vid is None:
            return render_template("error.html", fun_text="Video Clip does not exist!")
        if vid == "private":
            return render_template("error.html", fun_text="Video Clip is private!")
        return render_template("watch.html", video=get_video_by_id(request.args['id']), recommends=get_list_of_videos())
    return redirect("/content")


@app.route("/listen", methods=['GET'])
def listen():
    if 'id' in request.args:
        aud = get_audio_by_id(request.args['id'])
        if aud is None:
            return render_template("error.html", fun_text="Audio Clip does not exist!")
        if aud == "private":
            return render_template("error.html", fun_text="Audio Clip is private!")
        return render_template("listen.html", audio=aud)
    return redirect("/content")


@app.errorhandler(404)
def page_not_found(error):
    fun_text_options = ["You made a wrong turn!", "End of the road!", "Are you lost?", "May I help you?"]
    return render_template("error.html", fun_text=random.choice(fun_text_options),
                           technical_text="404 Error\nThe page requested is not found!")


@app.errorhandler(403)
def access_denied(error):
    fun_text_options = ["What are you up to?", "No you don't", "Get lost!"]
    return render_template("error.html", fun_text=random.choice(fun_text_options),
                           technical_text="403 Error\nThe item requested is forbidden!")


@app.route('/static/repository/videos/thumbnails/<filename>')
@app.route('/static/repository/videos/<filename>')
@app.route('/static/repository/audio/<filename>')
def access_protected_static_content(filename):
    mimetypes = list(zip(*list(request.accept_mimetypes)))[0]

    invalid_mimetype_flag = 'text/html' in mimetypes or 'application/xhtml+xml' in mimetypes or 'application/xml' in mimetypes

    if request.referrer is None or filename in request.referrer or invalid_mimetype_flag:  # Need to flush this out
        return access_denied(403)

    else:
        return send_file(app.root_path + request.path.replace("/", "\\"))


@app.before_request
def before_request():
    print("%s - - \"%s\"" % (request.base_url, request.user_agent))


if __name__ == '__main__':
    app.run()