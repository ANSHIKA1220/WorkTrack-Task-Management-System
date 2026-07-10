"""Employee names covering A–Z (international + Indian names)."""

import string

# Last names used across alphabets
LAST_NAMES = [
    "Sharma", "Patel", "Kumar", "Singh", "Gupta", "Reddy", "Mehta", "Joshi",
    "Desai", "Shah", "Rao", "Iyer", "Nair", "Kapoor", "Malhotra", "Chopra",
    "Verma", "Khan", "Das", "Roy", "Smith", "Johnson", "Williams", "Brown",
    "Davis", "Miller", "Wilson", "Taylor", "Anderson", "Thomas", "Jackson", "White",
]

# First names grouped by starting letter (A–Z)
FIRST_BY_LETTER = {
    "A": ["Aarav", "Aanya", "Aditya", "Ananya", "Arjun", "Aisha", "Akash", "Amrita", "Arun", "Avni",
          "Abhishek", "Anika", "Ashok", "Amit", "Anjali", "Arnav", "Ayush", "Aditi", "Alok", "Aman"],
    "B": ["Bhavesh", "Bhavna", "Bharat", "Bina", "Brijesh", "Bhavika", "Balaji", "Bindu", "Bobby", "Brandon",
          "Brian", "Brooke", "Benjamin", "Bella", "Bradley", "Bianca", "Barbara", "Blake", "Brenda", "Bruce"],
    "C": ["Chirag", "Charu", "Chetan", "Chitra", "Carlos", "Catherine", "Christopher", "Cynthia", "Cameron", "Chloe",
          "Charles", "Carol", "Connor", "Claire", "Caleb", "Carmen", "Colin", "Crystal", "Craig", "Cindy"],
    "D": ["Deepak", "Divya", "Dhruv", "Disha", "David", "Daniel", "Diana", "Donald", "Dorothy", "Dennis",
          "Derek", "Danielle", "Devin", "Diane", "Douglas", "Deborah", "Dylan", "Denise", "Doris", "Dale"],
    "E": ["Esha", "Ekta", "Emily", "Ethan", "Elizabeth", "Edward", "Eric", "Emma", "Evelyn", "Eugene",
          "Elena", "Elliot", "Esther", "Evan", "Elaine", "Enrique", "Erin", "Edgar", "Eva", "Earl"],
    "F": ["Farhan", "Fatima", "Frank", "Frances", "Felix", "Fiona", "Fred", "Florence", "Floyd", "Faith",
          "Fernando", "Freya", "Finn", "Faye", "Francis", "Fabian", "Farida", "Floyd", "Flora", "Faisal"],
    "G": ["Gaurav", "Gita", "Gopal", "Geeta", "George", "Grace", "Gregory", "Gloria", "Gabriel", "Gina",
          "Gerald", "Gayatri", "Gavin", "Gemma", "Grant", "Gwendolyn", "Gordon", "Giselle", "Garrett", "Greta"],
    "H": ["Harsh", "Hema", "Hitesh", "Harish", "Henry", "Helen", "Harold", "Hannah", "Howard", "Heather",
          "Hugo", "Holly", "Hector", "Hope", "Harvey", "Hazel", "Hunter", "Hilda", "Hamza", "Harini"],
    "I": ["Isha", "Irfan", "Indira", "Imran", "Isaac", "Isabella", "Ian", "Irene", "Ivan", "Ivy",
          "Ibrahim", "Ingrid", "Ishaan", "Iliana", "Ignacio", "Imani", "Irina", "Ida", "Ivan", "Indigo"],
    "J": ["Jatin", "Jyoti", "Jay", "Jasmine", "James", "Jennifer", "John", "Jessica", "Joseph", "Julia",
          "Jacob", "Janet", "Jason", "Joyce", "Jordan", "Judy", "Jack", "Joan", "Jesse", "Julie"],
    "K": ["Karan", "Kavya", "Krishna", "Kiran", "Kevin", "Karen", "Kenneth", "Kimberly", "Kyle", "Katherine",
          "Keith", "Kelly", "Kartik", "Komal", "Kamal", "Kristen", "Kurt", "Kavita", "Kunal", "Kriti"],
    "L": ["Lakshmi", "Lalit", "Leela", "Lokesh", "Larry", "Laura", "Lisa", "Linda", "Louis", "Lori",
          "Lawrence", "Lucy", "Leon", "Lena", "Liam", "Lata", "Lance", "Leah", "Logan", "Lynn"],
    "M": ["Manish", "Meera", "Mohit", "Maya", "Michael", "Mary", "Matthew", "Michelle", "Mark", "Maria",
          "Martin", "Melissa", "Manoj", "Madhuri", "Mukesh", "Monica", "Mason", "Megan", "Milan", "Myra"],
    "N": ["Nikhil", "Neha", "Naveen", "Nisha", "Nathan", "Nancy", "Nicholas", "Nicole", "Noah", "Natalie",
          "Neil", "Nora", "Nitin", "Namita", "Norman", "Nina", "Nigel", "Nandini", "Naveen", "Natasha"],
    "O": ["Om", "Ojas", "Olivia", "Oscar", "Owen", "Opal", "Omar", "Odette", "Orlando", "Olena",
          "Oliver", "Octavia", "Omkar", "Oindrila", "Otis", "Odessa", "Oleg", "Oona", "Osman", "Ophelia"],
    "P": ["Priya", "Pankaj", "Pooja", "Pranav", "Paul", "Patricia", "Peter", "Pamela", "Patrick", "Penny",
          "Philip", "Paula", "Parth", "Preeti", "Prakash", "Pallavi", "Pierre", "Piper", "Pablo", "Padma"],
    "Q": ["Quinn", "Qadir", "Queenie", "Quincy", "Qasim", "Quiana", "Quest", "Qamar", "Quentin", "Qiana",
          "Quinn", "Qadir", "Quinn", "Qamar", "Quincy", "Qasim", "Quiana", "Quentin", "Queenie", "Qamar"],
    "R": ["Rahul", "Riya", "Ravi", "Rekha", "Robert", "Rachel", "Richard", "Rebecca", "Ryan", "Rose",
          "Rajesh", "Radha", "Rohit", "Ritu", "Ralph", "Ruth", "Ronald", "Renee", "Rakesh", "Rashmi"],
    "S": ["Sanjay", "Sneha", "Suresh", "Sunita", "Sarah", "Steven", "Susan", "Samuel", "Sandra", "Scott",
          "Shreya", "Siddharth", "Sapna", "Sachin", "Simran", "Sean", "Sharon", "Sonia", "Satish", "Swati"],
    "T": ["Tarun", "Tanya", "Tejas", "Trisha", "Thomas", "Timothy", "Teresa", "Tyler", "Tina", "Tony",
          "Tara", "Tushar", "Tanvi", "Trevor", "Tammy", "Tracy", "Todd", "Tiffany", "Tariq", "Tanya"],
    "U": ["Umesh", "Uma", "Uday", "Urvashi", "Umar", "Ulrika", "Ursula", "Utkarsh", "Urvi", "Usman",
          "Ulysses", "Unity", "Uma", "Uday", "Ulrich", "Urvashi", "Umar", "Urvi", "Umesh", "Uma"],
    "V": ["Vikram", "Vidya", "Varun", "Vandana", "Vincent", "Victoria", "Virginia", "Vernon", "Violet", "Victor",
          "Vivek", "Vaishali", "Vijay", "Vani", "Vishal", "Veronica", "Valerie", "Vance", "Veda", "Vimal"],
    "W": ["William", "Walter", "Wayne", "Wendy", "Warren", "Whitney", "Wesley", "Wanda", "Wilson", "Willa",
          "Wade", "Winona", "Wyatt", "Winnie", "Wallace", "Wren", "Walter", "Willow", "Wade", "Wendell"],
    "X": ["Xavier", "Xena", "Xander", "Xiomara", "Xavier", "Xyla", "Xander", "Xenia", "Xavi", "Ximena",
          "Xavier", "Xena", "Xander", "Xiomara", "Xyla", "Xenia", "Xavi", "Ximena", "Xander", "Xena"],
    "Y": ["Yash", "Yashika", "Yuvraj", "Yamini", "Yusuf", "Yolanda", "Yvette", "Yogesh", "Yasmin", "Yvonne",
          "Yashwant", "Yamuna", "Yashpal", "Yashoda", "Yatin", "Yashvi", "Yashraj", "Yashasvi", "Yashdeep", "Yashmit"],
    "Z": ["Zara", "Zain", "Zoya", "Zubin", "Zachary", "Zoe", "Zane", "Zelda", "Zion", "Zara",
          "Zeeshan", "Zainab", "Zara", "Zubin", "Zachary", "Zoe", "Zain", "Zoya", "Zane", "Zelda"],
}


def generate_alphabet_names():
    """Build unique full names with at least one entry per letter A–Z."""
    names = []
    seen = set()
    li = 0

    for letter in string.ascii_uppercase:
        first_names = FIRST_BY_LETTER.get(letter, [letter])
        for first in first_names:
            last = LAST_NAMES[li % len(LAST_NAMES)]
            li += 1
            full = f"{first} {last}"
            if full not in seen:
                seen.add(full)
                names.append(full)

    return names


def generate_employee_names(count=500):
    """Return alphabet-covered names; extend if count exceeds generated set."""
    names = generate_alphabet_names()
    if len(names) >= count:
        return names[:count]
    return names
