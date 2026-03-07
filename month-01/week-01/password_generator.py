import argparse
import secrets
import string

def build_char_pool(use_upper, use_digits, use_special):
    # start with lowercase, conditionally add others
    # return the combined string
    char_pool = string.ascii_lowercase  
    if use_upper:
        char_pool += string.ascii_uppercase
    if use_digits:
        char_pool += string.digits
    if use_special:
        char_pool += string.punctuation

    return char_pool

def generate_password(length, char_pool):
    # generate a random password from the pool
    # ensure at least one char from each included type
    # shuffle and return as string
    if length <= 0:
        return ''
    
    password = ''.join(secrets.choice(char_pool) for _ in range(length))
    return password

def main():
    parser = argparse.ArgumentParser(description="Generate secure passwords")
    # add arguments: --length, --count, --no-upper, --no-digits, --no-special
    parser.add_argument('--length', type=int, default=12, help="Length of the password (default 12)")
    parser.add_argument('--count', type=int, default=1, help="How many passwords to generate (default 1)")
    parser.add_argument('--no-upper', action='store_true', help="Do not include uppercase letters")
    parser.add_argument('--no-digits', action='store_true', help="Do not include digits")
    parser.add_argument('--no-special', action='store_true', help="Do not include special characters")
    
    args = parser.parse_args()
    
    if args.length <= 0:
        print("Length must be greater than 0")
        return
    if args.count <= 0:
        print("Count must be greater than 0")
        return
    
    # build a pool of characters based on args
    char_pool = build_char_pool(not args.no_upper, not args.no_digits, not args.no_special)
    
    if not char_pool:
        print("Error: No characters to include in the password")
        return
    
    for _ in range(args.count):
        print(generate_password(args.length, char_pool))

if __name__ == "__main__":
    main()