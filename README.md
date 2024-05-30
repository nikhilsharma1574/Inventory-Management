<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Employee Details</title>
    <link rel="stylesheet" href="static\background.css">
    <link rel="stylesheet" href="static\styles.css">
    <link rel="stylesheet" href="static\admin.css">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">

</head>
<body>
    <div class="background">
        <div class="circle top-left"></div>
        <div class="circle top-right"></div>
    </div>
    

    <div class="glass-overlay"></div>
    <div class="sidenav">
        <!-- Content for side navigation bar goes here -->
        <h2>Sidebar</h2>
        <ul>
            <li>My Items</li>
            <li>All Items</li>
            <li>All Employees</li>
        </ul>
    </div>
    
    <div class="heading"><h2>Dashboard</h2></div>
    
    <div class="floating-search-bar">
        <div class="input-group">
            <input type="text" class="form-control" placeholder="Search...">
            <div class="input-group-append">
                <button class="btn btn-outline-secondary" type="button">Search</button>
            </div>
        </div>
    </div>

    <button class="additem btn btn-dark">Add Item</button>


    <div class="floating-filter-bar">
        <div class="input-group">
            <div class="input-group-append">
                <button class="btn btn-outline-secondary" type="button">All</button>
                <button class="btn btn-outline-secondary" type="button">Assigned</button>
                <button class="btn btn-outline-secondary" type="button">Unassigned</button>
            </div>
        </div>
    </div>
    
    <div class="floating-card">
        <h1>Employee Details</h1>
    <ul>
        <li><strong>UID:</strong> {{ user.UID }}</li>
        <li><strong>Name:</strong> {{ user.FullName }}</li>
        <li><strong>Email:</strong> {{ user.Email }}</li>
        <li><strong>Admin:</strong> {{ user.isAdmin }}</li>
    </ul>
    <h2>Assigned Items</h2>
    <ul>
        {% for item in user.assigned_items %}
            <li>{{ item.ItemName }} - {{ item.Quantity }}</li>
        {% endfor %}
    </ul>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>

</body>
</html>
