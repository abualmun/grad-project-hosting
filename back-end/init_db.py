import sys
print(sys.prefix)

import sqlite3
import json
import os

# Create database connection
def init_database():
    # Create the database file if it doesn't exist
    conn = sqlite3.connect('class_descriptions.db')
    cursor = conn.cursor()
    
    # Create the table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS class_descriptions (
        class_index INTEGER PRIMARY KEY,
        class_name TEXT NOT NULL,
        description TEXT NOT NULL
    )
    ''')
    
    # Load class names
    class_names = ["الحرم المكي"
                ,"العلا"
                ,"المسجد النبوي"
                ,"جبل أحد"
                ,"برج المملكة"
                ,"المصمك"
                ,"برج الفيصلية"
                ,"وادي حنيفة"
                ,"فقيه أكواريوم"
                ,"كورنيش جدة"
                ,"برج مياه الخبر"
                ,"مسجد قباء"
                ,"مسجد الراجحي"
                ,"المتحف الوطني"
                ]
    # try:
    #     with open('class_names.json', 'r') as f:
    #         class_names = json.load(f)
    # except:
    #     # If file doesn't exist, create placeholder class names
    #     class_names = [f"Class_{i}" for i in range(10)]
    #     with open('class_names.json', 'w') as f:
    #         json.dump(class_names, f)
    
    # Add sample descriptions for demonstration
    sample_descriptions = [
        "This is a detailed description for class 0. It provides information about what this class represents and its key characteristics.",
        "Class 1 represents objects with these specific features. This description helps users understand what has been identified in their image.",
        "When an image is classified as class 2, it means it contains these elements. This description provides more context about the classification.",
        "Class 3 is characterized by these specific traits. This detailed explanation helps users understand what the model has identified.",
        "Images classified as class 4 typically contain these features. This description elaborates on what this classification means.",
    ]
    
    # Populate the database with sample data
    for i, name in enumerate(class_names[:5]):  # Use only first 5 classes for sample data
        description = sample_descriptions[i] if i < len(sample_descriptions) else f"Detailed description for {name}"
        cursor.execute("INSERT OR REPLACE INTO class_descriptions (class_index, class_name, description) VALUES (?, ?, ?)",
                      (i, name, description))
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Database initialized with sample data")

if __name__ == "__main__":
    
    init_database()
