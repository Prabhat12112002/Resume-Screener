"""
Curated Skills Database for Resume Screening.

Organized by category for reliable skill extraction from resumes and job descriptions.
Skills are stored in lowercase for case-insensitive matching.
"""

SKILLS_DATABASE: dict[str, list[str]] = {
    # ── Programming Languages ──────────────────────────────────────────
    "programming_languages": [
        "python", "java", "javascript", "typescript", "c", "c++", "c#",
        "go", "golang", "rust", "ruby", "php", "swift", "kotlin", "scala",
        "r", "matlab", "perl", "lua", "dart", "elixir", "haskell",
        "objective-c", "shell", "bash", "powershell", "sql", "nosql",
        "html", "css", "sass", "less",
    ],

    # ── Frontend Frameworks & Libraries ────────────────────────────────
    "frontend": [
        "react", "reactjs", "react.js", "angular", "angularjs", "vue",
        "vuejs", "vue.js", "svelte", "next.js", "nextjs", "nuxt.js",
        "nuxtjs", "gatsby", "remix", "jquery", "bootstrap", "tailwind",
        "tailwindcss", "material ui", "material-ui", "chakra ui",
        "ant design", "redux", "mobx", "zustand", "webpack", "vite",
        "rollup", "parcel", "babel", "eslint", "prettier",
        "storybook", "figma", "adobe xd", "sketch",
    ],

    # ── Backend Frameworks ─────────────────────────────────────────────
    "backend": [
        "django", "flask", "fastapi", "express", "expressjs", "express.js",
        "nestjs", "nest.js", "spring", "spring boot", "springboot",
        "ruby on rails", "rails", "laravel", "asp.net", ".net", "dotnet",
        "gin", "fiber", "actix", "rocket", "phoenix", "koa", "hapi",
        "node.js", "nodejs", "node", "deno", "bun",
    ],

    # ── Databases ──────────────────────────────────────────────────────
    "databases": [
        "mysql", "postgresql", "postgres", "sqlite", "mongodb", "redis",
        "elasticsearch", "cassandra", "dynamodb", "couchdb", "neo4j",
        "mariadb", "oracle", "sql server", "mssql", "firebase",
        "firestore", "supabase", "cockroachdb", "influxdb",
        "timescaledb", "memcached",
    ],

    # ── Cloud & Infrastructure ─────────────────────────────────────────
    "cloud": [
        "aws", "amazon web services", "azure", "microsoft azure",
        "gcp", "google cloud", "google cloud platform",
        "heroku", "digitalocean", "linode", "vercel", "netlify",
        "cloudflare", "ec2", "s3", "lambda", "ecs", "eks",
        "cloud functions", "cloud run", "app engine",
    ],

    # ── DevOps & CI/CD ─────────────────────────────────────────────────
    "devops": [
        "docker", "kubernetes", "k8s", "terraform", "ansible", "puppet",
        "chef", "vagrant", "jenkins", "github actions", "gitlab ci",
        "circleci", "travis ci", "argo cd", "helm", "prometheus",
        "grafana", "datadog", "new relic", "splunk", "elk stack",
        "nginx", "apache", "caddy", "linux", "unix",
        "ci/cd", "ci cd", "continuous integration", "continuous deployment",
    ],

    # ── Data Science & Machine Learning ────────────────────────────────
    "data_science": [
        "machine learning", "deep learning", "artificial intelligence",
        "ai", "ml", "nlp", "natural language processing",
        "computer vision", "neural networks", "tensorflow", "pytorch",
        "keras", "scikit-learn", "sklearn", "pandas", "numpy", "scipy",
        "matplotlib", "seaborn", "plotly", "jupyter", "jupyter notebook",
        "data analysis", "data visualization", "data mining",
        "feature engineering", "model training", "model deployment",
        "hugging face", "transformers", "bert", "gpt", "llm",
        "large language models", "generative ai", "rag",
        "retrieval augmented generation", "langchain", "openai",
        "stable diffusion", "opencv", "spacy",
    ],

    # ── Data Engineering ───────────────────────────────────────────────
    "data_engineering": [
        "apache spark", "spark", "hadoop", "hive", "kafka",
        "apache kafka", "airflow", "apache airflow", "luigi",
        "etl", "data pipeline", "data warehouse", "data lake",
        "snowflake", "bigquery", "redshift", "databricks", "dbt",
        "data modeling",
    ],

    # ── Mobile Development ─────────────────────────────────────────────
    "mobile": [
        "react native", "flutter", "ionic", "xamarin", "android",
        "ios", "swiftui", "uikit", "jetpack compose", "kotlin multiplatform",
        "expo", "capacitor", "cordova",
    ],

    # ── Testing & QA ───────────────────────────────────────────────────
    "testing": [
        "unit testing", "integration testing", "e2e testing",
        "end-to-end testing", "jest", "mocha", "chai", "cypress",
        "selenium", "playwright", "puppeteer", "pytest", "unittest",
        "testng", "junit", "rspec", "tdd", "bdd",
        "test-driven development", "behavior-driven development",
        "load testing", "performance testing", "jmeter",
    ],

    # ── Version Control & Collaboration ────────────────────────────────
    "version_control": [
        "git", "github", "gitlab", "bitbucket", "svn", "mercurial",
        "jira", "confluence", "trello", "asana", "slack",
        "microsoft teams", "agile", "scrum", "kanban", "sprint",
    ],

    # ── API & Architecture ─────────────────────────────────────────────
    "api_architecture": [
        "rest", "restful", "rest api", "graphql", "grpc", "soap",
        "websocket", "websockets", "microservices", "monolith",
        "serverless", "event-driven", "message queue", "rabbitmq",
        "celery", "design patterns", "solid principles", "mvc",
        "mvvm", "clean architecture", "domain-driven design", "ddd",
        "api gateway", "swagger", "openapi", "postman",
    ],

    # ── Security ───────────────────────────────────────────────────────
    "security": [
        "oauth", "oauth2", "jwt", "json web token", "authentication",
        "authorization", "encryption", "ssl", "tls", "https",
        "owasp", "penetration testing", "vulnerability assessment",
        "cybersecurity", "sso", "single sign-on", "ldap",
        "role-based access control", "rbac",
    ],

    # ── Soft Skills ────────────────────────────────────────────────────
    "soft_skills": [
        "leadership", "communication", "teamwork", "problem solving",
        "problem-solving", "critical thinking", "time management",
        "project management", "mentoring", "collaboration",
        "presentation", "stakeholder management", "decision making",
        "conflict resolution", "adaptability", "creativity",
    ],
}


def get_all_skills() -> set[str]:
    """Return a flat set of all skills from the database."""
    all_skills: set[str] = set()
    for category_skills in SKILLS_DATABASE.values():
        all_skills.update(category_skills)
    return all_skills


def get_skills_by_category(category: str) -> list[str]:
    """Return skills for a specific category."""
    return SKILLS_DATABASE.get(category, [])


def get_multi_word_skills() -> set[str]:
    """Return skills that contain more than one word (need special matching)."""
    return {skill for skill in get_all_skills() if " " in skill or "-" in skill}


def get_single_word_skills() -> set[str]:
    """Return skills that are a single word."""
    return {skill for skill in get_all_skills() if " " not in skill and "-" not in skill}
