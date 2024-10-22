This is a Flask web application that manages seasonal flavors, ingredient inventory, and customer suggestions using SQLite as the database.


## Features

- Add, update, and delete seasonal flavors.
- Add, update, and delete ingredients in the inventory.
- Submit customer suggestions, delete suggestions

**steps to run the application** : 

  1) Python should be installed
   
  2)  git clone https://github.com/yourusername/your-repo.git
   
  3)  install requirements(flask)
  4)  cd your-repo
  5)  python app.py
  6)  access the app using http://127.0.0.1:5000/



## Edge Cases Handled

1. **Empty Input**: Returns a 400 error if the flavor name or ingredient is empty.
2. **Duplicate Entries**: Returns a 409 error if the flavor or ingredient already exists.
3. **Negative Stock**: Returns a 400 error if stock is negative when adding an ingredient.
4. **General Database Errors**: Catches and handles exceptions during database operations gracefully.
