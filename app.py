import os,re,sqlite3
from datetime import datetime
from flask import Flask,render_template,request,flash,redirect,url_for
from werkzeug.utils import secure_filename
from pypdf import PdfReader
from docx import Document
app=Flask(__name__,template_folder=".",static_folder=".",static_url_path="/static"); app.secret_key=os.environ.get("SECRET_KEY","change-me")
os.makedirs("/tmp/uploads",exist_ok=True); DB="/tmp/resume_analyzer.db"
ROLES={
"Data Analyst":["python","sql","excel","power bi","tableau","statistics","pandas","data visualization","communication"],
"Web Developer":["html","css","javascript","react","git","responsive design","api","testing"],
"AI Engineer":["python","machine learning","pytorch","tensorflow","scikit-learn","numpy","pandas","deep learning","nlp"],
"Cloud Engineer":["aws","azure","gcp","docker","kubernetes","linux","networking","terraform","ci/cd"],
"Python Developer":["python","sql","git","api","flask","django","testing","oop"],
"Software Engineer":["python","java","c++","git","data structures","algorithms","testing","sql","api"]}
SECTIONS={"contact":["email","phone","contact"],"education":["education","degree","university","college"],"skills":["skills","technical skills","technologies"],"projects":["projects"],"experience":["experience","internship","work history"],"certifications":["certifications","certificates"]}
ALLSKILLS=sorted(set(s for v in ROLES.values() for s in v))
with sqlite3.connect(DB) as c:c.execute("CREATE TABLE IF NOT EXISTS analyses(id INTEGER PRIMARY KEY,filename,role,score,ats,created,feedback)")
def extract(p,ext):
 if ext=="pdf":return "\n".join(x.extract_text() or "" for x in PdfReader(p).pages)
 return "\n".join(x.text for x in Document(p).paragraphs)
def has(text,words):return any(re.search(r"(?<!\w)"+re.escape(x)+r"(?!\w)",text.lower()) for x in words)
def analyze(text,role):
 low=text.lower(); sect={k:has(low,v) for k,v in SECTIONS.items()}
 skills=[s for s in ALLSKILLS if has(low,[s])]
 checks={"Contact information":sect["contact"],"Education":sect["education"],"Skills section":sect["skills"],"Projects section":sect["projects"],"Experience/internship":sect["experience"],"Certifications":sect["certifications"],"Resume length":350<=len(text.split())<=1200,"Action language":any(x in low for x in ["developed","built","created","implemented","improved","designed","analyzed"]),"Readable text":len(text.strip())>=250,"Technical keywords":len(skills)>=3}
 score=sum(10 for x in checks.values() if x)
 req=ROLES[role]; matched=[x for x in req if has(low,[x])]; missing=[x for x in req if x not in matched]; ats=round(100*len(matched)/len(req))
 tips=[f"Consider adding a clearly labelled {k.lower()} section." for k,v in checks.items() if not v and k not in ["Resume length","Action language","Readable text","Technical keywords"]]
 if not checks["Resume length"]:tips.append("Keep your resume concise, usually around 1–2 pages.")
 if not checks["Action language"]:tips.append("Use action verbs and measurable outcomes where possible.")
 if not checks["Readable text"]:tips.append("Ensure your document contains enough selectable text.")
 if not checks["Technical keywords"]:tips.append("Add relevant technical skills you genuinely possess.")
 feedback=["Scores are heuristic—not hiring predictions."]
 if missing:feedback.append("For "+role+", consider demonstrating these skills if you have them: "+", ".join(missing)+".")
 if not sect["projects"]:feedback.append("Add projects with the problem, tools and your contribution.")
 if not sect["experience"]:feedback.append("If you lack formal experience, highlight practical projects or coursework.")
 feedback.append("Use truthful, specific bullet points and quantify outcomes where possible.")
 return score,checks,matched,missing,ats,tips,feedback
@app.route("/",methods=["GET","POST"])
def index():
 if request.method=="POST":
  f=request.files.get("resume"); role=request.form.get("role","AI Engineer")
  if not f or not f.filename:flash("Choose a file.");return redirect(url_for("index"))
  fn=secure_filename(f.filename); ext=fn.rsplit(".",1)[-1].lower()
  if ext not in ["pdf","docx"]:flash("Upload PDF or DOCX.");return redirect(url_for("index"))
  path=os.path.join("/tmp/uploads",fn);f.save(path)
  try:text=extract(path,ext)
  except Exception:flash("Could not parse file.");return redirect(url_for("index"))
  if not text.strip():flash("No text found. Scanned PDFs may require OCR.");return redirect(url_for("index"))
  score,checks,matched,missing,ats,tips,feedback=analyze(text,role)
  with sqlite3.connect(DB) as c:c.execute("INSERT INTO analyses(filename,role,score,ats,created,feedback) VALUES(?,?,?,?,?,?)",(fn,role,score,ats,datetime.now().isoformat(), "\n".join(feedback)))
  return render_template("results.html",filename=fn,role=role,score=score,checks=checks,matched=matched,missing=missing,ats=ats,tips=tips,feedback=feedback,words=len(text.split()))
 with sqlite3.connect(DB) as c:history=c.execute("SELECT filename,role,score,ats,created FROM analyses ORDER BY id DESC LIMIT 8").fetchall()
 return render_template("index.html",roles=list(ROLES),history=history)
@app.route("/about")
def about():return render_template("about.html")
if __name__=="__main__":app.run(debug=True)
