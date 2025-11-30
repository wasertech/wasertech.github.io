import toml
import json
import os
import qrcode

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

    # Certifications
    data['certifications'] = []
    for filename in sorted(os.listdir('data/certifications')):
        if filename.endswith('.toml'):
            data['certifications'].append(toml.load(os.path.join('data/certifications', filename)))

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