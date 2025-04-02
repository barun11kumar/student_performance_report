def is_student(user):
    """Check if user is a student"""
    return user.groups.filter(name='Student').exists()

def is_teacher(user):
    """Check if user is a teacher"""
    return user.groups.filter(name='Teacher').exists()

def is_admin(user):
    """Check if user is an admin"""
    return user.is_superuser 