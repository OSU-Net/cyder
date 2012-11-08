def tablefy_users(users):
    """
    Build matrix that can be printed as table along with headers and urls
    Mimics the tablefy utility for the user model.
    Hard to use the other tablefy utility since we did not subclass user model
    """

    headers = []
    matrix = []
    urls   = []
    if not users:
        return (None, None, None)

    # Build the headers
    headers = ['Name', 'First Name', 'Last Name', 'Email', 'Phone Number']

    # Build the matrix and urls
    for user in users:
        urls.append('/cyuser/' + str(user.id))

        matrix.append([
            user.username,
            user.first_name,
            user.last_name,
            user.email,
            user.get_profile().phone_number
        ])

    return (headers, matrix, urls)
