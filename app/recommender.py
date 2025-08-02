
from .models import Repository
from collections import Counter

def skill_recommender(user, resume_data):
    recommendations = {}
    resume_skills = set(resume_data.extracted_skills)

    # skill gaps
    skill_gaps = resume_data.skill_gaps
    recommendations["skill_gaps"] = skill_gaps

    # skills in commites but not resume
    repos = Repository.query.filter_by(user_id=user.id).all()
    commit_summaries = set()
    for repo in repos:
        summary = repo.serialize().get("commit_summary")
        commit_summaries.update(summary)
    hidden_strengths = commit_summaries - resume_skills
    recommendations["hidden_strengths"] = list(hidden_strengths)

    # adjacent skills

    # most demonstrated skills, boost these in the resume
    skill_counts = Counter(resume_data.supported_skills) + Counter(list(commit_summaries))
    recommendations["skill_counts"] = skill_counts



    return recommendations



