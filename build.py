import toml
import json
import os
import subprocess
import qrcode
from datetime import datetime

def fetch_github_contributions(username="wasertech", min_stars=100, exclude_repos=None):
    """
    Fetch merged PRs to external repos using gh CLI.
    Returns list of contributions sorted by stars (most popular first).
    """
    if exclude_repos is None:
        exclude_repos = []
    
    try:
        # GraphQL query to get merged PRs with repo info
        query = '''
        {
          user(login: "%s") {
            pullRequests(first: 100, states: MERGED) {
              nodes {
                title
                url
                mergedAt
                repository {
                  nameWithOwner
                  owner { login }
                  stargazerCount
                }
              }
            }
          }
        }
        ''' % username
        
        result = subprocess.run(
            ['gh', 'api', 'graphql', '-f', f'query={query}'],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode != 0:
            print(f"Warning: gh CLI failed: {result.stderr}")
            return []
        
        data = json.loads(result.stdout)
        prs = data.get('data', {}).get('user', {}).get('pullRequests', {}).get('nodes', [])
        
        # Filter: external repos only, above min_stars, not in exclude list
        contributions = {}
        for pr in prs:
            repo = pr['repository']
            repo_name = repo['nameWithOwner']
            owner = repo['owner']['login']
            stars = repo['stargazerCount']
            
            # Skip own repos and excluded repos
            if owner == username or repo_name in exclude_repos:
                continue
            
            # Skip low-star repos
            if stars < min_stars:
                continue
            
            # Group by repo, count PRs
            if repo_name not in contributions:
                contributions[repo_name] = {
                    'project': repo_name,
                    'url': f"https://github.com/{repo_name}",
                    'stars': stars,
                    'pr_count': 0,
                    'prs': [],
                    'latest_merge': None,
                }
            
            contributions[repo_name]['pr_count'] += 1
            contributions[repo_name]['prs'].append({
                'title': pr['title'],
                'url': pr['url'],
                'merged_at': pr['mergedAt']
            })
            
            # Track latest merge date
            merge_date = pr['mergedAt']
            if contributions[repo_name]['latest_merge'] is None or merge_date > contributions[repo_name]['latest_merge']:
                contributions[repo_name]['latest_merge'] = merge_date
        
        # Sort by stars (descending)
        sorted_contribs = sorted(contributions.values(), key=lambda x: x['stars'], reverse=True)
        
        return sorted_contribs
        
    except subprocess.TimeoutExpired:
        print("Warning: gh CLI timed out")
        return []
    except Exception as e:
        print(f"Warning: Failed to fetch contributions: {e}")
        return []


def build_data():
    data = {}

    # Profile
    data['profile'] = toml.load('data/profile/profile.toml')

    # Contact
    contact_data = toml.load('data/contact/contact.toml')
    data['contact'] = contact_data

    # Skills
    data['skills'] = toml.load('data/skills/skills.toml')['skills']

    # Languages
    data['languages'] = toml.load('data/languages/languages.toml')['languages']

    # Interests
    data['interests'] = toml.load('data/interests/interests.toml')['interests']

    # Experiences
    data['experiences'] = []
    for filename in sorted(os.listdir('data/experiences')):
        if filename.endswith('.toml'):
            data['experiences'].append(toml.load(os.path.join('data/experiences', filename)))

    # Education
    if os.path.exists('data/education/education.toml'):
        data['education'] = toml.load('data/education/education.toml')['education']
    else:
        data['education'] = []

    # Certifications
    data['certifications'] = []
    for filename in sorted(os.listdir('data/certifications')):
        if filename.endswith('.toml'):
            data['certifications'].append(toml.load(os.path.join('data/certifications', filename)))

    # Contributions (auto-fetched from GitHub)
    contrib_config = {}
    if os.path.exists('data/contributions/contributions.toml'):
        contrib_config = toml.load('data/contributions/contributions.toml')
    
    min_stars = contrib_config.get('min_stars', 100)
    exclude_repos = contrib_config.get('exclude_repos', [])
    manual_contribs = contrib_config.get('contributions', [])
    
    # Fetch from GitHub
    print("Fetching contributions from GitHub...")
    github_contribs = fetch_github_contributions(
        username="wasertech",
        min_stars=min_stars,
        exclude_repos=exclude_repos
    )
    print(f"  Found {len(github_contribs)} external repos with {min_stars}+ stars")
    
    # Merge manual and auto-fetched
    data['contributions'] = {
        'manual': manual_contribs,
        'github': github_contribs
    }

    # Portfolio/Projects
    if os.path.exists('data/portfolio/projects.toml'):
        data['portfolio'] = toml.load('data/portfolio/projects.toml')['projects']
    else:
        data['portfolio'] = []

    # Articles
    if os.path.exists('data/articles/articles.toml'):
        data['articles'] = toml.load('data/articles/articles.toml')['articles']
    else:
        data['articles'] = []

    # Media
    # if os.path.exists('data/media/media.toml'):
    #     data['media'] = toml.load('data/media/media.toml')['media']
    # else:
    data['media'] = []

    # Sections
    data['sections'] = toml.load('data/sections/sections.toml')
    
    with open('static/cv_data.json', 'w') as f:
        json.dump(data, f, indent=2)
        
    print("cv_data.json built successfully.")

    # Generate vCard
    vcard = f"""BEGIN:VCARD
VERSION:3.0
N:Waser;Danny;;;
FN:Danny Waser
EMAIL;TYPE=INTERNET:{contact_data['email']}
TEL;TYPE=CELL:{contact_data['phone']}
ADR;TYPE=HOME:;;{contact_data['address']}
URL:{contact_data['website']}
URL:{contact_data['github']}
URL:{contact_data['gitlab']}
URL:{contact_data['linkedin']}
URL:{contact_data['docker']}
URL:{contact_data['discourse']}
URL:{contact_data['youtube']}
URL:{contact_data['matrix']}
END:VCARD"""
    with open('static/waser.vcf', 'w') as f:
        f.write(vcard)
    print("waser.vcf built successfully.")

    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(vcard)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save('static/images/qrc.png')
    print("qrc.png built successfully.")


if __name__ == '__main__':
    build_data()