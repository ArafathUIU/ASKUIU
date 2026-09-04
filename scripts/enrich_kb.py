"""Enrich and update the UIU Knowledge Base with verified high-density facts.

Usage:
    python scripts/enrich_kb.py
"""

import os
import pandas as pd
from datetime import datetime, timezone

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(PROJECT_ROOT, "app", "rag", "data", "AskUIU.csv")

VERIFIED_CHUNKS = [
    # 1. Leadership & Authorities
    {
        "Title": "UIU Leadership and Authorities - Complete Directory",
        "Source": "https://www.uiu.ac.bd/authorities/",
        "Category": "administration",
        "Text": (
            "United International University (UIU) Leadership and Key Authorities Directory:\n"
            "- Chancellor: The Honorable President of the People's Republic of Bangladesh.\n"
            "- Chairman, Board of Trustees: Mr. Hasan Mahmood Raja (United Group).\n"
            "- Vice Chancellor: Prof. Dr. Md. Abul Kashem Mia.\n"
            "- Pro Vice Chancellor: Prof. Dr. K. M. A. Salam.\n"
            "- Treasurer: Engr. Md. Abdul Moqaddem.\n"
            "- Registrar: Dr. Md. Zulfiqur Rahman.\n"
            "- Director (Coordination): Prof. A. S. M. Salahuddin.\n"
            "- Proctor: Dr. Rumana Afrin (Associate Professor and Head, Department of Civil Engineering).\n"
            "- Proctorial Committee Members: Prof. A. S. M. Salahuddin (Director of Coordination), "
            "Dr. Tahmina Foyez (Head, Dept. of Pharmacy), Dr. Shantanu Kumar Saha (Head, Dept. of EDS), "
            "Lt. Col. Md. Zayed Hossain (Retd.) (Joint Director, Operations), Mr. Jakowan (Assistant Professor, SoBE), "
            "Ms. Sadia Islam (Assistant Professor, Dept. of CSE), Ms. Tasnim Jahan Tumpa (Lecturer, Economics), "
            "Ms. Sanzida Akhter (Deputy Controller of Examinations, Member Secretary).\n"
            "- Directorate of Career Counseling & Student Affairs (DCCSA): Mr. Md. Aminul Islam (Deputy Director).\n"
            "Official Contact: United City, Madani Avenue, Badda, Dhaka 1212. Phone: +88 09604-848-848."
        )
    },
    # 2. Department Heads & Deans
    {
        "Title": "Department Heads and Academic Leadership - UIU",
        "Source": "https://www.uiu.ac.bd/academics/schools-institutes/",
        "Category": "academics",
        "Text": (
            "Department Heads and School Leadership at United International University (UIU):\n"
            "- Head of Department of Computer Science & Engineering (CSE): Dr. Mohammad Nurul Huda (Professor & Head, Dept. of CSE).\n"
            "- Head of Department of Electrical & Electronic Engineering (EEE): Dr. Kaled Masukur Rahman (Professor & Head, Dept. of EEE).\n"
            "- Head of Department of Civil Engineering: Dr. Rumana Afrin (Associate Professor & Head, Dept. of Civil Engineering, also UIU Proctor).\n"
            "- Head of Department of Pharmacy: Dr. Tahmina Foyez (Associate Professor & Head, Department of Pharmacy, School of Life Sciences).\n"
            "- Head of Department of English: Dr. Md. Kamrul Hasan (Associate Professor & Head, Department of English).\n"
            "- Director of BSc in Data Science Program: Dr. Jannatun Noor Mukta (Associate Professor, Dept. of CSE & Director, Data Science Program).\n"
            "- Head of Department of Environment & Development Studies (EDS): Dr. Shantanu Kumar Saha (Associate Professor & Head, Dept. of EDS).\n"
            "- School of Business & Economics (SoBE): Offers BBA, BBA in AIS, Economics, MBA, and Executive MBA (EMBA).\n"
            "- School of Science & Engineering (SoSE): Encompasses Dept. of CSE, Dept. of EEE, and Dept. of Civil Engineering.\n"
            "- School of Humanities & Social Sciences (SoHS): Encompasses Dept. of English and Media Studies & Journalism (MSJ).\n"
            "- School of Life Sciences: Encompasses Dept. of Pharmacy and Dept. of Biotechnology & Genetic Engineering (BGE)."
        )
    },
    # 3. Comprehensive Undergraduate Tuition Fees Table
    {
        "Title": "Undergraduate Tuition Fees, Credits, and Cost Breakdown - UIU",
        "Source": "https://www.uiu.ac.bd/admission/tuition-fees-payment-policies/tuition-fees-waiver/",
        "Category": "admission",
        "Text": (
            "Complete Undergraduate Tuition Fees and Credit Breakdown at UIU:\n"
            "Per Credit Fee for all undergraduate programs is Tk. 6,500/-.\n"
            "Admission Fee: Tk. 20,000/- (non-refundable down payment during admission).\n"
            "Caution Money for ID Card: Tk. 2,000/- (refundable upon graduation).\n"
            "Trimester Fee: Tk. 6,500/- per trimester (for 12-trimester 4-year programs).\n"
            "Semester Fee: Tk. 9,750/- per semester (for 8-semester B.Pharm program).\n\n"
            "Program Details and Total Cost Estimates:\n"
            "1. BSc in Computer Science and Engineering (BSCSE): 141 Total Credits | 12 Trimesters | "
            "Without Waiver: Tk. 10,14,500 | With 25% Waiver: Tk. 7,95,125 | With 50% Waiver: Tk. 5,75,750.\n"
            "2. Bachelor of Business Administration (BBA): 125 Total Credits | 12 Trimesters | "
            "Without Waiver: Tk. 9,10,500 | With 25% Waiver: Tk. 7,12,250 | With 50% Waiver: Tk. 5,14,000.\n"
            "3. BBA in Accounting and Information Systems (AIS): 125 Total Credits | 12 Trimesters | "
            "Without Waiver: Tk. 9,10,500 | With 25% Waiver: Tk. 7,12,250 | With 50% Waiver: Tk. 5,14,000.\n"
            "4. BSc in Economics (BSECO): 122 Total Credits | 12 Trimesters | "
            "Without Waiver: Tk. 8,91,000 | With 25% Waiver: Tk. 6,97,625 | With 50% Waiver: Tk. 5,04,250.\n"
            "5. BSc in Environment and Development Studies (BSSEDS): 123 Total Credits | 12 Trimesters | "
            "Without Waiver: Tk. 8,97,500 | With 25% Waiver: Tk. 7,07,375 | With 50% Waiver: Tk. 5,17,250.\n"
            "6. BSc in Data Science (BSDS): 140 Total Credits | 12 Trimesters | Per Credit Fee: Tk. 6,500 | Total without waiver: ~Tk. 10,08,000.\n"
            "7. BSc in Electrical and Electronic Engineering (BSEEE): 140 Total Credits | 12 Trimesters | Per Credit Fee: Tk. 6,500 | Total without waiver: ~Tk. 10,08,000.\n"
            "8. BSc in Civil Engineering: 144 Total Credits | 12 Trimesters | Per Credit Fee: Tk. 6,500 | Total without waiver: ~Tk. 10,34,000.\n"
            "9. Bachelor of Pharmacy (B.Pharm): 160 Total Credits | 8 Semesters (Bi-semester) | Per Credit Fee: Tk. 6,500 | "
            "Semester Fee: Tk. 9,750 per semester | Lab Fee: Tk. 5,000 per semester.\n"
            "10. BA in English: 123 Total Credits | 12 Trimesters | Per Credit Fee: Tk. 6,500 | Total without waiver: ~Tk. 8,97,500.\n"
            "11. BSS in Media Studies & Journalism (MSJ): 123 Total Credits | 12 Trimesters | Per Credit Fee: Tk. 6,500.\n"
            "12. BSc in Biotechnology & Genetic Engineering (BGE): 140 Total Credits | 12 Trimesters | Lab Fee: Tk. 2,000 per trimester.\n\n"
            "Payment Installments: Tk. 20,000 partial payment before course registration in each trimester; "
            "remaining balance payable in three installments at 40%, 30%, and 30% rates."
        )
    },
    # 4. Comprehensive Graduate Tuition Fees Table
    {
        "Title": "Graduate Programs Tuition Fees and Credit Structure - UIU",
        "Source": "https://www.uiu.ac.bd/admission/tuition-fees-payment-policies/tuition-fees-waiver/",
        "Category": "admission",
        "Text": (
            "Graduate Programs Tuition Fees, Credit Requirements, and Costs at UIU:\n"
            "Per Credit Fee for graduate courses is Tk. 6,500/-.\n"
            "1. Master of Business Administration (MBA):\n"
            "   - Total Credits: 60 Credits (or 30 Credits for BBA graduates with waivers) | 6 Trimesters.\n"
            "   - Cost (60 Credits): Without Waiver: Tk. 4,49,000 | With 25% Waiver: Tk. 3,51,500.\n"
            "   - Cost (30 Credits): Without Waiver: Tk. 2,41,000 | With 25% Waiver: Tk. 1,92,250.\n"
            "2. Executive MBA (EMBA):\n"
            "   - Total Credits: 45 Credits (or 30 Credits) | 5 Trimesters.\n"
            "   - Cost (45 Credits): Without Waiver: Tk. 3,45,000 | With 25% Waiver: Tk. 2,71,875.\n"
            "   - Cost (30 Credits): Without Waiver: Tk. 2,41,000 | With 25% Waiver: Tk. 1,92,250.\n"
            "3. Master of Science in CSE (MSCSE):\n"
            "   - Total Credits: 36 Credits | 4 Trimesters.\n"
            "   - Cost: Without Waiver: Tk. 2,80,000 | With 25% Waiver: Tk. 2,21,500 (Theory based), "
            "Tk. 2,31,250 (Project based), Tk. 2,50,750 (Thesis based).\n"
            "4. Master of Science in Economics (MSECO):\n"
            "   - Total Credits: 30 Credits | 4 Trimesters | Without Waiver: Tk. 2,41,000.\n"
            "5. Master in Development Studies (MDS):\n"
            "   - Total Credits: 39 Credits | 4 Trimesters | Without Waiver: Tk. 2,99,500."
        )
    },
    # 5. Scholarship & Tuition Fee Waiver Policies
    {
        "Title": "UIU Scholarship, Tuition Fee and Other Fees Waiver Policy",
        "Source": "https://www.uiu.ac.bd/admission/tuition-fees-payment-policies/scholarship-tuition-fee-and-other-fees-waiver-policy/",
        "Category": "admission",
        "Text": (
            "UIU Scholarship, Tuition Fee and Waiver Policies:\n"
            "UIU disburses approximately Tk. 10 to 12 Crore per year in scholarships and waivers, one of the highest in Bangladesh.\n\n"
            "1. Merit Waiver at Admission (Undergraduate Entry):\n"
            "- SSC and HSC GPA 5.00 (with 4th subject): 20% to 50% tuition fee waiver.\n"
            "- Golden GPA 5.00 in both SSC and HSC: Up to 50% to 100% tuition waiver.\n"
            "- English Medium: 5 'A's in O-Level and 2 'A's in A-Level receive up to 50%-100% waiver.\n"
            "- UIU Admission Test Toppers: Merit scholarships up to 100% waiver.\n\n"
            "2. Trimester Exam Result Scholarships:\n"
            "- The top 3% to 5% students in each department/batch with high trimester GPA/CGPA receive 25%, 50%, or 100% tuition waiver for the subsequent trimester.\n"
            "- Requirements: Must complete full registered credits (minimum 9-12 credits) without any 'I' (Incomplete) grade or retake in that trimester.\n\n"
            "3. Special and Quota Waivers:\n"
            "- Freedom Fighter Quota: 100% tuition waiver for children of verified Freedom Fighters (as per UGC and Government of Bangladesh rules).\n"
            "- Sibling and Spouse Waiver: 20% to 40% waiver on tuition fees for the second sibling/spouse studying concurrently at UIU.\n"
            "- Remote & High Poverty Area Waiver: Financial assistance for students hailing from Upazilas classified under 'Very High Poverty Level' by the Bangladesh Bureau of Statistics (BBS).\n"
            "- Retake Course Waiver: Course fee for each retake/repeat is waived by 50% for the first time."
        )
    },
    # 6. Academic Calendar, Trimester System & Grading Scale
    {
        "Title": "Academic System, Grading Scale and Performance Evaluation - UIU",
        "Source": "https://www.uiu.ac.bd/academics/grading-performance-evaluation/",
        "Category": "academics",
        "Text": (
            "UIU Academic System and Grading Scale:\n"
            "1. Trimester System: UIU operates on a three-trimester per year system:\n"
            "   - Spring Trimester: January – April\n"
            "   - Summer Trimester: May – August\n"
            "   - Fall Trimester: September – December\n"
            "   (Note: Department of Pharmacy operates on a Bi-Semester system with Spring and Fall semesters).\n\n"
            "2. Grading Scale & Grade Points:\n"
            "- 80% and above: Grade A (4.00 Grade Point, Outstanding)\n"
            "- 75% to <80%: Grade A- (3.67 Grade Point, Excellent)\n"
            "- 70% to <75%: Grade B+ (3.33 Grade Point, Very Good)\n"
            "- 65% to <70%: Grade B (3.00 Grade Point, Good)\n"
            "- 60% to <65%: Grade B- (2.67 Grade Point, Satisfactory)\n"
            "- 55% to <60%: Grade C+ (2.33 Grade Point, Above Average)\n"
            "- 50% to <55%: Grade C (2.00 Grade Point, Average - Minimum passing grade for prerequisites)\n"
            "- 40% to <50%: Grade D (1.00 Grade Point, Pass)\n"
            "- Below 40%: Grade F (0.00 Grade Point, Fail)\n"
            "- I: Incomplete, W: Withdrawn.\n\n"
            "3. Graduation & CGPA Requirements:\n"
            "- A minimum Cumulative Grade Point Average (CGPA) of 2.00 on a 4.00 scale is required for graduation.\n\n"
            "4. Academic Probation Policy:\n"
            "- If a student's CGPA falls below 2.00, they are placed on Academic Probation.\n"
            "- If the student remains on probation for 3 consecutive trimesters without raising CGPA to 2.00, they are subject to academic suspension or dismissal.\n\n"
            "5. Course Retake Policy:\n"
            "- A student can retake a course if they received a grade of B- or lower.\n"
            "- First retake of a course receives a 50% tuition fee waiver."
        )
    },
    # 7. Undergraduate Admission Requirements & Eligibility
    {
        "Title": "Undergraduate Admission Requirements and Eligibility - UIU",
        "Source": "https://www.uiu.ac.bd/admission/admission-requirements/",
        "Category": "admission",
        "Text": (
            "Undergraduate Admission Requirements and Criteria at UIU:\n"
            "1. General Eligibility:\n"
            "- Minimum GPA of 2.50 individually in SSC and HSC (or 2nd Division) with a total combined GPA of at least 6.00.\n"
            "- For Science and Engineering Programs (BSc in CSE, Data Science, EEE, and Civil Engineering): Candidates must have passed Physics and Mathematics in HSC, Diploma, or A-Level.\n"
            "- For English Medium (GCE): Minimum 5 subjects in O-Level with an average GPA of 2.50, and 2 subjects in A-Level with an average GPA of 2.00. No 'E' grade is accepted.\n"
            "- Diploma Holders: Minimum GPA 2.50 in Diploma in Engineering from the Bangladesh Technical Education Board (BTEB).\n"
            "- Validity: HSC, Diploma, or A-Level results must have been published within the last 5 years.\n\n"
            "2. Admission Test Procedure:\n"
            "- Applicants must sit for a written admission test and an interview.\n"
            "- Written test evaluates Mathematics, Physics, and English for engineering programs; and English, Mathematics, and Analytical aptitude for business programs.\n"
            "- Direct admission / test exemption is available for applicants with high SAT scores.\n\n"
            "3. Required Documents at Admission:\n"
            "- Original and photocopies of SSC and HSC mark sheets and certificates.\n"
            "- 4 copies of recent passport-size color photographs.\n"
            "- National ID card (NID) or Birth Certificate copy.\n"
            "- Blood group laboratory report."
        )
    },
    # 8. Campus Location, Infrastructure & Campus Life
    {
        "Title": "UIU Permanent Campus Location, Facilities and Student Life",
        "Source": "https://www.uiu.ac.bd/about-uiu/uiu-campus/",
        "Category": "campus_life",
        "Text": (
            "UIU Permanent Campus Location and Infrastructure:\n"
            "- Campus Address: United City, Madani Avenue, Badda, Dhaka 1212, Bangladesh (approximately 2.5 km east of the US Embassy, located on 100 Feet Madani Avenue road).\n"
            "- Campus Land Area: 25 bighas of land with a state-of-the-art green, fully air-conditioned, environment-friendly architectural design.\n"
            "- Academic & Administrative Shift: The university moved entirely to this permanent campus in February 2018.\n\n"
            "Campus Facilities:\n"
            "- Central Library: Fully automated library with digital e-resources, private study cubicles, IEEE Xplore, ScienceDirect, and discussion rooms.\n"
            "- Sports Facilities: Full-sized international football ground, cricket practice nets, basketball court, indoor games zone.\n"
            "- Gymnasium: Modern gym equipped with advanced workout machines and certified physical fitness trainers.\n"
            "- Cafeteria: Large hygienic food court providing subsidized meals and snacks for students, faculty, and staff.\n"
            "- Medical Center: On-campus medical clinic with certified full-time physicians providing emergency first aid and healthcare support.\n"
            "- Research Laboratories: Advanced Intelligent Multidisciplinary Systems Lab (AIMS Lab), Centre for Energy Research (CER), "
            "Centre for Artificial Intelligence and Robotics (CAIR), VLSI Lab, IoT Lab, Concrete Lab, Surveying Lab, and Power Systems Lab."
        )
    },
    # 9. Student Transportation & Shuttle Bus Routes
    {
        "Title": "UIU Student Transportation Service and Shuttle Routes",
        "Source": "https://www.uiu.ac.bd/uiu-transportation-service/",
        "Category": "campus_life",
        "Text": (
            "UIU Student Transportation Service:\n"
            "UIU operates an extensive, heavily subsidized student transportation bus fleet connecting the permanent campus with major hubs of Dhaka city.\n\n"
            "Key Bus Routes:\n"
            "- Shuttle Service: Continuous AC and non-AC shuttle buses operate between Notun Bazar (Madani Avenue crossing) and UIU Campus throughout the day.\n"
            "- Mirpur Route: Covers Mirpur-10, Mirpur-1, Sony Cinema, ECB Chattar, Kalshi, and Kuril to UIU.\n"
            "- Uttara Route: Covers House Building, Azampur, Rajlakshmi, Airport, Khilkhet, and Kuril to UIU.\n"
            "- Dhanmondi / City Center Route: Covers Dhanmondi, Science Lab, Farmgate, Mohakhali, and Gulshan to UIU.\n"
            "- South Dhaka Route: Covers Motijheel, Jatrabari, Malibagh, Rampura, and Banasree to UIU.\n"
            "Students can register for trimester transport service via the UCAM portal or purchase single-ride tokens."
        )
    },
    # 10. UIU Mars Rover Team & URC Achievements
    {
        "Title": "UIU Mars Rover Team Achievements and Robotics - Team MAVEN",
        "Source": "https://cse.uiu.ac.bd/news/asia-no-1-world-no-3-celebrating-excellence-uiu-mars-rover-team-achieves-at-urc-2026/",
        "Category": "campus_life",
        "Text": (
            "UIU Mars Rover Team (Team MAVEN) Achievements:\n"
            "- Global Rankings: Ranked **Asia No. 1** and **World No. 3** at the University Rover Challenge (URC) organized by The Mars Society "
            "at the Mars Desert Research Station (MDRS) in Utah, USA.\n"
            "- Motto & Slogan: 'History now has a new name: UIU' and 'This is more than a ranking. This is ambition engineered.'\n"
            "- Competition Details: Competes in the University Rover Challenge (URC) and Anatolian Rover Challenge (ARC), competing against top universities from the USA, Poland, Australia, and Canada.\n"
            "- Engineering Capabilities: The rover features autonomous navigation using computer vision and GPS, robotic arm manipulation for precision equipment servicing, "
            "science payload for geological soil analysis and life detection, and extreme rock mobility on high-traction suspension.\n"
            "- Student Innovation: The team is composed of multidisciplinary engineering students from the Department of CSE and Department of EEE, mentored by university professors."
        )
    },
    # 11. Student Clubs and Forums
    {
        "Title": "Student Clubs, Forums and Co-Curricular Activities - UIU",
        "Source": "https://www.uiu.ac.bd/campus-life/clubs-forums/",
        "Category": "campus_life",
        "Text": (
            "Active Student Clubs and Forums at UIU:\n"
            "Co-curricular activities are managed by the Directorate of Career Counseling and Student Affairs (DCCSA):\n"
            "- UIU Computer Club (UIUCC): Hosts competitive programming contests, hackathons, and tech workshops.\n"
            "- UIU Robotics Club: Builds autonomous robots, drones, and hosts National Robotics Competitions.\n"
            "- UIU Mars Rover Team (MAVEN): International rover engineering and astronautics team.\n"
            "- UIU Cultural Club: Organizes music, dance, theatrical performances, and Bengali cultural festivals.\n"
            "- UIU Sports Club: Organizes UIU Premier League (cricket, football), table tennis, and badminton tournaments.\n"
            "- UIU Debating Club (UIUDC): Regularly wins national and inter-university parliamentary debate tournaments.\n"
            "- UIU Photography Club (UIUPC): Organizes photo exhibitions and technical photography workshops.\n"
            "- UIU Model United Nations Club (UIUMUN): International diplomacy and MUN conferences.\n"
            "- UIU Social Services Club: Blood donation camps, winter clothes distribution, and relief projects.\n"
            "- UIU Finance Forum & UIU Marketing Forum: Professional workshops and corporate competitions."
        )
    },
    # 12. Contact Directory & Helpdesk
    {
        "Title": "UIU Contact Information, Admissions Office and Helpdesk Directory",
        "Source": "https://www.uiu.ac.bd/contact-us/",
        "Category": "administration",
        "Text": (
            "Official Contact Information and Helpdesk at UIU:\n"
            "- Permanent Campus Address: United City, Madani Avenue, Badda, Dhaka 1212, Bangladesh.\n"
            "- General Hotline: +88 09604-848-848\n"
            "- Admissions Office Mobile: +88 01759 039 465, +88 01759 039 498, +88 01759 039 451, +88 01914 001 470\n"
            "- General Email: info@uiu.ac.bd\n"
            "- Admissions Email: admissions@uiu.ac.bd\n"
            "- Website: https://www.uiu.ac.bd\n"
            "- Office Hours: Saturday to Thursday, 9:00 AM to 5:00 PM (Closed on Fridays and government holidays).\n"
            "- Extension Contacts: Admissions (Ext: 1301-1305), Student Affairs/DCCSA (Ext: 1202-1206), Controller of Examinations (Ext: 1407-1408)."
        )
    }
]


def enrich_knowledge_base():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"Knowledge base CSV not found at {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)
    initial_count = len(df)
    print(f"Loaded existing knowledge base with {initial_count} rows.")

    # Remove outdated low-quality snippets or broken duplicates
    bad_snippets = [
        "I accomplished my goal by finishing my studies",
        "With the course of time, I had start enjoying",
    ]
    for snip in bad_snippets:
        df = df[~df["Text"].str.contains(snip, na=False)]

    cleaned_count = len(df)
    print(f"Cleaned up {initial_count - cleaned_count} low-quality snippet rows.")

    # Check for existing enriched titles to avoid duplicate injection
    existing_titles = set(df["Title"].dropna().tolist())
    new_rows = []
    now_str = datetime.now(timezone.utc).isoformat()

    for item in VERIFIED_CHUNKS:
        if item["Title"] in existing_titles:
            # Update existing row text
            idx = df[df["Title"] == item["Title"]].index
            df.loc[idx, "Text"] = item["Text"]
            df.loc[idx, "Source"] = item["Source"]
            df.loc[idx, "Category"] = item["Category"]
            df.loc[idx, "LastCrawled"] = now_str
            print(f"Updated existing chunk: {item['Title']}")
        else:
            new_rows.append({
                "Text": item["Text"],
                "Title": item["Title"],
                "Source": item["Source"],
                "Category": item["Category"],
                "ChunkIndex": 0,
                "LastCrawled": now_str
            })
            print(f"Adding new enriched chunk: {item['Title']}")

    if new_rows:
        df_new = pd.DataFrame(new_rows)
        df = pd.concat([df, df_new], ignore_index=True)

    # Save enriched CSV
    df.to_csv(CSV_PATH, index=False)
    print(f"Enriched knowledge base saved to {CSV_PATH} (Total rows: {len(df)}).")


if __name__ == "__main__":
    enrich_knowledge_base()
