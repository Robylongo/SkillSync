
from .models import Repository


SKILL_ADJACENCY = {
    # ---- Programming Languages ----
    "python": ["numpy", "pandas", "scikit-learn", "tensorflow", "flask", "django", "fastapi"],
    "java": ["spring", "maven", "hibernate"],
    "javascript": ["node.js", "react", "vue", "angular", "express"],
    "typescript": ["react", "next.js", "angular", "nestjs"],
    "c": ["c++", "embedded systems"],
    "c++": ["c", "qt", "openmp"],
    "go": ["gin", "grpc", "docker"],
    "rust": ["tokio", "actix", "wasm"],

    # ---- Web Frameworks ----
    "flask": ["python", "jinja2", "sqlalchemy"],
    "django": ["python", "postgresql", "rest api"],
    "fastapi": ["python", "pydantic", "uvicorn"],
    "express": ["node.js", "mongodb", "jwt"],
    "spring": ["java", "spring boot", "hibernate"],

    # ---- Frontend ----
    "react": ["javascript", "typescript", "redux", "next.js"],
    "vue": ["javascript", "vuex", "nuxt.js"],
    "angular": ["typescript", "rxjs"],
    "next.js": ["react", "typescript"],
    "tailwind": ["react", "next.js", "vue"],

    # ---- Databases ----
    "postgresql": ["sql", "django", "fastapi"],
    "mysql": ["sql", "php", "laravel"],
    "mongodb": ["node.js", "express", "mongoose"],
    "redis": ["python", "flask", "celery"],

    # ---- DevOps / Cloud ----
    "docker": ["kubernetes", "ci/cd", "aws", "gcp"],
    "kubernetes": ["docker", "helm", "aws", "gcp"],
    "aws": ["lambda", "ec2", "s3", "cloudformation"],
    "gcp": ["bigquery", "cloud functions", "firebase"],
    "azure": ["devops", "cosmos db"],

    # ---- Data Science / ML ----
    "numpy": ["python", "pandas", "scikit-learn"],
    "pandas": ["python", "numpy", "matplotlib"],
    "scikit-learn": ["python", "numpy", "pandas", "tensorflow"],
    "tensorflow": ["keras", "python", "scikit-learn"],
    "keras": ["tensorflow", "python"],
    "pytorch": ["torchvision", "python"],
    "matplotlib": ["pandas", "numpy"],

    # ---- Tools ----
    "git": ["github actions", "gitlab ci", "docker"],
    "github actions": ["git", "ci/cd"],
    "ci/cd": ["docker", "kubernetes"],
}



from collections import defaultdict

def build_parent_map(skill_map):
    """
    Builds a map of each skill -> its parent(s) based on SKILL_ADJACENCY.
    """
    parent_map = defaultdict(set)
    for parent, related in skill_map.items():
        for child in related:
            parent_map[child].add(parent)
    return parent_map


def smart_recommend_parent_priority_auto(resume_skills, commit_skills, skill_map=SKILL_ADJACENCY, min_overlap=2):
    all_skills = {s.lower() for s in list(resume_skills) + list(commit_skills)}
    parent_map = build_parent_map(skill_map)

    recommendations = []
    covered_by_parent = set()

    for skill, related in skill_map.items():
        # Only skip if skill is NOT a parent AND has a known parent
        if skill not in skill_map and any(parent in all_skills for parent in parent_map.get(skill, [])):
            continue
        if skill in covered_by_parent:
            continue

        overlap = len(all_skills & set(related))
        if skill in all_skills or overlap >= min_overlap:
            new_skills = [r for r in related if r not in all_skills]
            if new_skills:
                recommendations.append((skill, new_skills))
                covered_by_parent.update(related)

    return recommendations


def skill_recommender(user, resume_data):

    resume_skills = set(resume_data.extracted_skills)
    skill_gaps = resume_data.skill_gaps

    # Hidden strengths
    repos = Repository.query.filter_by(user_id=user.id).all()
    commit_summaries = set()
    for repo in repos:
        summary = repo.serialize().get("commit_summary", [])
        commit_summaries.update(summary)
    hidden_strengths = commit_summaries - resume_skills

    # Adjacent skills
    recs = smart_recommend_parent_priority_auto(resume_skills, commit_summaries)

    friendly_lines = []
    if skill_gaps:
        friendly_lines.append(
            f"<p>📌 <b>Skill Gaps:</b> These are skills that show up in your resume's skill section but isnt backed up by any work experience/projcets: {', '.join(skill_gaps)}.</p>"
        )
    if hidden_strengths:
        friendly_lines.append(
            f"<p>💡 <b>Hidden Strengths:</b> These appear in your commits but not your resume — consider adding them: {', '.join(hidden_strengths)}.</p>"
        )
    if recs:
        for base_skill, new_skills in recs:
            friendly_lines.append(
                f"<p>➡️ Since you already know <b>{base_skill}</b>, you could explore: {', '.join(new_skills)}.</p>"
            )

    formatted_html = "".join(friendly_lines)

    return {
        "raw": {
            "skill_gaps": list(skill_gaps),
            "hidden_strengths": list(hidden_strengths),
            "smart_recommendations": [
                {"base_skill": base_skill, "recommended_skills": new_skills}
                for base_skill, new_skills in recs
            ]
        },
        "formatted_html": formatted_html
    }





