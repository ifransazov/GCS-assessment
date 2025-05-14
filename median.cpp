#include <iostream>
#include <vector>
#include <stdexcept>

class Activity2
{
private:

    //sorts a vector of integers via bubble sort
    void bubbleSort(std::vector<int>& numbers)
    {
        // if given vector is empty, just return
        if(numbers.empty())
        {
            return;
        }

        bool swapped;
        for (int i = 0; i < numbers.size() - 1; i++)
        {
            swapped = false;
            
            for (int j = 0; j < numbers.size() - 1 - i; j++)
            {
                if(numbers[j] > numbers[j + 1])
                {
                    //swap
                    int temp = numbers[j];
                    numbers[j] = numbers[j + 1];
                    numbers[j + 1] = temp;
                    
                    //note the swap
                    swapped = true;
                }
            }

            if (!swapped)
            {
                break; //early break, nohting else has been swapped, so it is sorted
            }
        }
    }

public: 
    //sort and find median function from pseudocode
    double sortAndFindMedian(const std::vector<int>& input)
    {
        // input handling
        if(input.empty())
        {
            std::cerr << "Error: empty input given\n";
            throw std::invalid_argument("No median for an empty list");
        }

        //make a local copy to not alter users input array
        std::vector<int> numbers = input;

        //sort
        bubbleSort(numbers);

        // n as length of numbers
        int n = numbers.size();

        // if even number of elements get average of middle 2
        if (n % 2 == 0)
        {
            //ensure no rounding by dividing by 2.0 instead of 2
            return (numbers[(n/2) - 1] + numbers[n/2]) / 2.0;
        }
        // else, get the median
        else
        {
            return numbers[n/2];
        }

    }

};


int main() {
    Activity2 solver;
    std::vector<int> numbers;

    // predefined test cases
    std::vector<std::vector<int>> tests = 
    {
        {5, 2, 9, 4, 7}, //expect 5
        {10, 8, 2, 4}, //expect 6
        {1}, // expect 1
        {-1, 529, -5, -50, 52}, //expect -1
        { }, // expect error
        {1, 2, 3, 4, 5, 6, 7, 8, 9} // expect 5
    };

    std::cout << "pre-made tests\n";

    for (auto& test : tests) 
    {
        for (int x : test) std::cout << x << ' ';
        
        try 
        {
            double m = solver.sortAndFindMedian(test);
            std::cout << "median = " << m << "\n";
        } 
        
        catch (const std::invalid_argument& ex) 
        {
            std::cerr << "Input error: " << ex.what() << "\n";
        }
    }

    return 0;
}