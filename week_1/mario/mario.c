#include <stdio.h>
#include <cs50.h>
int user_input();

int main()
{   
    int number = user_input();
    for (int i = 0; i < number; i++)
    {   
        for (int k  = i + 1; number - k > 0; k++)
        {
            printf(" ");
        }
        for (int k = 0; k <= i; k++)
        {
            printf("#");
        }
        printf("  ");
        for (int k = 0; k <= i; k++)
        {
            printf("#");
        }
        printf("\n");
    }

    
}

int user_input()
{
    int number = get_int("Height: ");
    while (number < 1 || number > 8)
    {
        number = get_int("height: ");
    }
    return number;
}

