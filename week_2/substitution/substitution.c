#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <cs50.h>

int main(int argc, string argv[])
{
    // if first cl argument not exist
    if (! argv[1])
    {
        printf("no argument");
        return 1;
    }

    // if there are more than one arguments
    if (argc != 2)
    {
        printf("more than one argument");
        return 1;
    }
    
    // check key

    string key = argv[1];

    // if key is not contains 26 characters
    if (strlen(key) != 26)
    {
        printf("your key is not 26 characters length");
        return 1;
    }

    // if key contains any character wich is not alphabetic
    // or if key contains repeatable characters
   
    bool seen[26] = {0};

    for (int i = 0; i < 26; i++)
    {
        // if character is not letter
        if (! isalpha(key[i]))
        {
            printf("non alphabetic character in key");
            return 1;
        }

        // make character lowercase
        key[i] = tolower((unsigned char)key[i]);

        // if letter is in seen array
        if (seen[key[i] - 97])
        {
            printf("key has repeatable charcters");
            return 1;
        }

        // add character to seen array

        seen[key[i] - 97] = true;

    }


    
    string plain_text = get_string("plaintext:");
    char chipher_text[strlen(plain_text)];
    for (int i = 0; i < strlen(plain_text); i++)
    {
        
        if (isalpha(plain_text[i]))
        {
            if islower(plain_text[i])
            {
                chipher_text[i] = key[plain_text[i] - 97];
            }
            else
            {
                chipher_text[i] = toupper(key[plain_text[i] - 65]);
            }
        }
        else
        {
            chipher_text[i] = plain_text[i];
        }    
    }
    printf("ciphertext:");
    for (int c = 0; c < strlen(plain_text); c++)
    {
        printf("%c", chipher_text[c]);
    }
    printf("\n");
    return 0;
}



