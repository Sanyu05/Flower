Problems/Need to do:
1)Some numeric data may be converted to string if it has strange numbers in it - for example $134.97M  
current version handles M - Million, B-Billion, K-Thousand

2) Need to test with more data sets to see where the data does not get converted correctly - need to clean but on a case by case basis?
3) Need to implement text file name input from user
4) Basic cleaning functions used - some of them are AIed lol

- main.py has print fuction to verify if data is getting converted properly
- data_clean fucntion is slightly complicated :( 
- We can give multiple options for data visualization - just make functions
- only check for fields is one should be string and the other is numeric (cannot compare two numerics or strings)
- if we have time we can make GUI 

How to use:
Download the .csv file and place it in the "Flower" folder - where main.py is
Change the file name in imf.simple_csv_loader to the name of the file
run the program to show summary of the data and to see how it is stored 

Each column is a proper NumPy array
print(type(data['First Name']))            # <class 'numpy.ndarray'>
print(data['First Name'].shape)            # (100,) - 100 elements
print(data['First Name'].dtype)            # <U8 - Unicode string, max 8 chars

This is how you access individual columns and the data stored in them - 'First Name' is name of the column


