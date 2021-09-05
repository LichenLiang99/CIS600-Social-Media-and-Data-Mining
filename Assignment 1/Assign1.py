class mathclass:

    #initialize 
    def __init__(self, a, b):
        self.a = a
        print("initializing a: " + str(a))
        self.b = b
        print("initializing b: " + str(b))

    #calculate sum of a and b
    def get_sum(self):
        sum = self.a + self.b
        print("The sum of the two numbers you have entered is " + str(sum))
        return sum

    #calculate a^b
    def get_power(self):
        result = self.a ** self.b
        print("power of a^b is: " + str(result))
        return result
        
    #calculate (a*b)^i where i is 1 to 10 and add them to a list
    def list_product_powers(self):
        some_list = []
        product = self.a * self.b

        for i in range(0,10):
            some_list.append(product**i)

        return some_list

    #given a list, return a new list that have values less than the limit, default limit is 0
    def filter_less_than(self, some_list, limit = 0):
        new_list = []
        for i in range(len(some_list)):
            if some_list[i] < limit:
                new_list.append(some_list[i])
        
        return new_list

    #given a list, return a new list that have values greater than the limit, default limit is 0
    def filter_greater_than(self, some_list, limit = 0):
        new_list = [some_list[i] for i in range(len(some_list)) if some_list[i] > limit]
        return new_list

    #get quotient of a/b, if dividing by 0 raise error
    def get_quotient(self):
        try: 
            quotient = int(self.a)/int(self.b)
        except ZeroDivisionError:
            print("Dividing by zero")
            return
        return quotient

        
if  __name__  ==  "__main__":

    #test to check all functions work properly
    test = mathclass(4,2)
    adding = test.get_sum()
    print(adding)

    power = test.get_power()
    print(power)

    power_list = test.list_product_powers()
    print(power_list)

    filtered_list = test.filter_less_than(power_list, 5000)
    print('values less than 5000')
    print(filtered_list)

    filtered_list2 = test.filter_greater_than(power_list, 5000)
    print('values more than 5000')
    print(filtered_list2)

    quotient = test.get_quotient()
    print('quotient of a/b is ' + str(quotient))

    #ask user to input 2 numbers and initialize in mathclass class
    #try entering b to be 0
    print("please input 2 numbers: ")
    print("a : ")
    a = int(input())
    print("b : ")
    b = int(input())

    test2 = mathclass(a,b)
    quotient2 = test2.get_quotient()
    print(quotient2)

    adding2 = test2.get_sum()
    print(adding2)

    power2 = test2.get_power()
    print(power2)

    power_list2 = test2.list_product_powers()
    print(power_list2)

    filtered_list3 = test.filter_less_than(power_list2, 50)
    print('values less than 50')
    print(filtered_list3)

    filtered_list4 = test.filter_greater_than(power_list2, 6812)
    print('values more than 6812')
    print(filtered_list4)

    #--------------------------------------------------------------
    #dictionary
    new_dictionary = {'apple':2,'pear':4,'banana':3}
    
    key = new_dictionary.keys()
    value = new_dictionary.values()
    new_dict = {key:value for (key,value) in new_dictionary.items()}
    print(new_dict)