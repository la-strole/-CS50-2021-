#include <stdio.h>
#include <cs50.h>
#include <string.h>
#include <ctype.h>
#include <math.h>

int main(void)
{
    string text = get_string("Text: ");
    int length = strlen(text);
    int letters = 0;
    int words = 1;
    int sequence = 0;
    
    for (int i = 0; i < length; i++)
    {
        char character = text[i];

        if (isalpha(character))
        {
            letters += 1;
        }

        else if (character == ' ')
        {
            words += 1;
        }

        else if (character == '.' || character == '?' || character == '!')
        {
            sequence += 1;
        }
    }

    float L = ((float)letters / words) * 100;
    printf("L = %f\n", L);
    float S = ((float)sequence / words) * 100;
    printf("S = %f\n", S);
    double index = 0.0588 * L - 0.296 * S - 15.8;

    if (index >= 16)
    {
        printf("Grade 16+\n");
    }
    else if (index < 1)
    {
        printf("Before Grade 1\n");
    }
    else
    {
        printf("Grade %i\n", (int)round(index));
    }

}