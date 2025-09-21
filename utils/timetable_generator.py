def generate_personalized_timetable(school_timetable, habits):
    personalized = {}

    for day, slots in school_timetable.items():
        personalized[day] = []
        total_study_hours = habits.hours_per_day

        for slot in slots:
            if total_study_hours > 0:
                personalized[day].append({
                    "course": slot.get("course", "General Study"),
                    "start": slot["end"],
                    "end": f"{int(slot['end'].split(':')[0]) + 1}:00",
                    "type": "study"
                })
                total_study_hours -= 1

        if habits.difficult_courses:
            difficult_list = habits.difficult_courses.split(",")
            for course in difficult_list:
                if total_study_hours > 0:
                    personalized[day].append({
                        "course": course.strip(),
                        "start": habits.preferred_time,
                        "end": "Flexible",
                        "type": "extra study"
                    })
                    total_study_hours -= 1

    return personalized

