#include <stdio.h>
#include <cs50.h>
#include <math.h>



int main()
{
    long user_number = get_long("Number: ");
    long number = user_number;
    int check = 0;
    int length, n;
    string name = "INVALID";

    for (int i = 0; number != 0; i++)
    {
        if (i % 2 == 0)
        {
            check += number % 10;
        }
        else
        {
            n = (number % 10) * 2;
            if (n >= 10)
            {
                check += n % 10;
                n = n / 10;
                check += n;
            }
            else
            {
                check += n;
            }

        }
        number = number / 10;
        length = i + 1;
    }

    // printf("for test: length = %i, check_cum = %i\n", length, check);
    // if it is VISA by digit length
    if (length == 13)
    {
        int first_number = user_number / pow(10, length - 1);
        if (first_number == 4)
        {
            name = "VISA";
        }
    
    }
    // if it is AMEX
    else if (length == 15)
    {
        int first_number = user_number / pow(10, length - 2);
        if (first_number == 34 || first_number == 37)
        {
            name = "AMEX";
        }
    }
    // if it is MASTERCARD or VISA with 16 digits
    else if (length == 16)
    {
        int first_number = user_number / pow(10, length - 2);
        if (first_number == 51 || first_number == 52 || first_number == 53 || first_number == 54 || first_number == 55)
        {
            name = "MASTERCARD";
        }
        else if ((first_number / 10) == 4)
        {
            name = "VISA";
        } 
    }

    
    if (check % 10 == 0)
    {
        printf("%s\n", name);
    }
    else
    {
        printf("INVALID\n");
    }
}