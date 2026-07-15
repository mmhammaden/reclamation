# Generated migration to normalize matricules to uppercase and handle duplicates

from django.db import migrations


def normalize_matricules(apps, schema_editor):
    """
    Normalize all matricules to uppercase and handle duplicates.
    For duplicate matricules (different cases), keep the one with more complete data
    and delete the others.
    """
    User = apps.get_model('users', 'User')
    
    # Get all users
    users = User.objects.all()
    
    # Group users by uppercase matricule
    matricule_groups = {}
    for user in users:
        upper_matricule = user.matricule.upper()
        if upper_matricule not in matricule_groups:
            matricule_groups[upper_matricule] = []
        matricule_groups[upper_matricule].append(user)
    
    # Process each group
    for upper_matricule, group_users in matricule_groups.items():
        if len(group_users) > 1:
            # Multiple users with same matricule (different cases) - need to merge
            # Keep the one with most complete data (has first_name, last_name, etc.)
            group_users.sort(key=lambda u: (
                bool(u.first_name),
                bool(u.last_name),
                bool(u.email),
                u.date_joined
            ), reverse=True)
            
            # Keep the first one (most complete), delete others
            keep_user = group_users[0]
            keep_user.matricule = upper_matricule
            keep_user.save(update_fields=['matricule'])
            
            for user_to_delete in group_users[1:]:
                user_to_delete.delete()
        else:
            # Single user - just normalize to uppercase
            user = group_users[0]
            if user.matricule != upper_matricule:
                user.matricule = upper_matricule
                user.save(update_fields=['matricule'])


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_hierarchical_structure'),
    ]

    operations = [
        migrations.RunPython(normalize_matricules, migrations.RunPython.noop),
    ]
