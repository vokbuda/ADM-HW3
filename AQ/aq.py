def find_path_with_required_cells( required_cells):
    # Before it is necessary to sort array
    required_cells = sorted(required_cells)
      # Target cell is the last
    
    # setup initial position
    current_x, current_y = 0, 0
    path = []

    # iterate over cells in sorted array
    for target_x, target_y in required_cells:
        # Calculate the differences in x and y
        delta_x = target_x - current_x
        delta_y = target_y - current_y
        
        # If we need to move left or down, it's impossible
        if delta_x < 0 or delta_y < 0:
            return "NO"
        
        # Add 'R' for each step to the right
        path.append('R' * delta_x)
        # Add 'U' for each step up
        path.append('U' * delta_y)
        
        # Update the current position
        current_x, current_y = target_x, target_y

    # print result in case if it is possible
    return "YES\n" + ''.join(path)


if __name__=='__main__':
    
    number_cases=int(input())
    for i in range(number_cases):
        num_rows=int(input())
        arr_test=[]
        for x in range(num_rows):
            test_row=input().split()
            test_row=[int(test_row[0]),int(test_row[1])]
            arr_test.append(test_row)
        print(find_path_with_required_cells( arr_test))
            
       
        

