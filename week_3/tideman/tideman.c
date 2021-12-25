#include <cs50.h>
#include <stdio.h>
#include <string.h>

// Max number of candidates
#define MAX 9

// preferences[i][j] is number of voters who prefer i over j
int preferences[MAX][MAX];

// locked[i][j] means i is locked in over j
bool locked[MAX][MAX];

// Each pair has a winner, loser
typedef struct
{
    int winner;
    int loser;
}
pair;

// Array of candidates
string candidates[MAX];
pair pairs[MAX * (MAX - 1) / 2];

int pair_count;
int candidate_count;

// Function prototypes
bool vote(int rank, string name, int ranks[]);
void record_preferences(int ranks[]);
void add_pairs(void);
void sort_pairs(void);
void lock_pairs(void);
void print_winner(void);
int loop_test(int node, int winner, int visited_nodes[candidate_count], int *r, int *visited_nodes_index);

int main(int argc, string argv[])
{
    // Check for invalid usage
    if (argc < 2)
    {
        printf("Usage: tideman [candidate ...]\n");
        return 1;
    }

    // Populate array of candidates
    candidate_count = argc - 1;
    if (candidate_count > MAX)
    {
        printf("Maximum number of candidates is %i\n", MAX);
        return 2;
    }
    for (int i = 0; i < candidate_count; i++)
    {
        candidates[i] = argv[i + 1];
    }

    // Clear graph of locked in pairs
    for (int i = 0; i < candidate_count; i++)
    {
        for (int j = 0; j < candidate_count; j++)
        {
            locked[i][j] = false;
        }
    }

    pair_count = 0;
    int voter_count = get_int("Number of voters: ");

    // Query for votes
    for (int i = 0; i < voter_count; i++)
    {
        // ranks[i] is voter's ith preference
        int ranks[candidate_count];

        // Query for each rank
        for (int j = 0; j < candidate_count; j++)
        {
            string name = get_string("Rank %i: ", j + 1);

            if (!vote(j, name, ranks))
            {
                printf("Invalid vote.\n");
                return 3;
            }
        }

        record_preferences(ranks);

        printf("\n");
    }

       
    add_pairs();
    sort_pairs();
    lock_pairs();
    print_winner();
    return 0;
}

// Update ranks given a new vote
bool vote(int rank, string name, int ranks[])
{
    // if name is valid
    
    bool valid_name = false;

    for (int i = 0; i < candidate_count; i++)
    {
        if (strcmp(name, candidates[i]) == 0)
        {
            ranks[rank] = i;
            return true;
        }
    }
    return false;
}

// Update preferences given one voter's ranks
void record_preferences(int ranks[])
{
    // from the first place
    for (int i = 0; i < candidate_count - 1; i++)
    {
        for (int j = i + 1; j < candidate_count; j++)
        {
            preferences[ranks[i]][ranks[j]] += 1; 
        }
    }
    return;
}

// Record pairs of candidates where one is preferred over the other
void add_pairs(void)
{   
    int  pairs_index = 0;
    
    for (int row = 0; row < candidate_count; row++)
    {
        for (int column = 0; column < candidate_count; column++)
        {
            if (preferences[row][column] > preferences[column][row])
            {
                pairs[pairs_index].winner = row;
                pairs[pairs_index].loser = column;
                pairs_index++;
                pair_count++;
            }
        }
    }
    return;
}

// Sort pairs in decreasing order by strength of victory
void sort_pairs(void)
{
    pair tmp_value;
    for (int j = 0; j < pair_count - 1; j++)
    {
        for (int i = j + 1; i < pair_count; i++)
        {
            if (preferences[pairs[i].winner][pairs[i].loser] > preferences[pairs[j].winner][pairs[j].loser])
            {
                tmp_value = pairs[j];
                pairs[j] = pairs[i];
                pairs[i] = tmp_value;

            }
        }
    }
    return;
}

// Lock pairs into the candidate graph in order, without creating cycles
void lock_pairs(void)
{   
    for (int pair_num = 0; pair_num < pair_count; pair_num++)
    {
        // initialize visited nodes array
        int visited_nodes[candidate_count];
        for (int i = 0; i < candidate_count; i++)
        {
            visited_nodes[i] = -1;
        }
        // initialize variables for loop test function
        int result = 1;
        int *result_p = &result;
        int visited_nodes_index = 0;
        int *visited_nodes_index_p = &visited_nodes_index;
        int winner = pairs[pair_num].winner;
        int loser = pairs[pair_num].loser;

        // test
        // printf("winner=%i, loser=%i\n", winner, loser);

        if (loop_test(loser, winner, visited_nodes, result_p, visited_nodes_index_p) == 1)
        {
            // lock edge
            locked[winner][loser] = true;
            // test
            for (int i = 0; i < candidate_count; i++)
                for (int j = 0; j < candidate_count; j++)
                    {
                        printf("[%i][%i] = %d\n", i, j, locked[i][j]);
                    }
        }
      
    }

    return;
}

// loop test
int loop_test(int node, int winner, int visited_nodes[candidate_count],  int *r, int *visited_nodes_index)
{

    // test
    /*
    printf("loop test: node = %i, result = %i, visited nodes = ", node, *r);

    for (int i = 0; i < candidate_count; i++)
    {
        printf("%i, ", visited_nodes[i]);
    }
    printf("\n");
    */

    int answer = 1;

    // base case 
  
    if (node == winner)
    {   
        *r = 0;
        return 0;
    }

    else if (r == 0)
    {
        return 0;
    }

    // went trough child in connectivity matrix 
    for (int i = 0; i < candidate_count; i++)
    {
        if (locked[node][i] == true)
        {
            bool visited = false;
            for (int j = 0; j < candidate_count; j++)
            {
                if (visited_nodes[j] == node)
                {
                    visited = true;
                }
            }
        
            if (visited == false)
            {
                visited_nodes[*visited_nodes_index] = node;
                *visited_nodes_index += 1;
                return loop_test(i, winner, visited_nodes, r, visited_nodes_index);
            }
        }
    }
    
    return *r;
}


// Print the winner of the election
void print_winner(void)
{
    for (int j = 0; j < candidate_count; j++)
    {
        bool winner = true;
        
        for (int i = 0; i < candidate_count; i++)
        {
            if (locked[i][j] == true)
            {   
                winner = false;
                break;
            }
        }
        if (winner == true)
        {
            printf("%s\n", candidates[j]);
        }

    }
    return;
}

