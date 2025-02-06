import os
from random import randint, choices, random, choice
from string import digits 
from typing import List

class Grabuge:

    def __init__(self):
        """Constructor
        """
        self.__flag: str = "RT{LS_is_for_L00S3R}"
        self.__parent_dir: str = 'challFile' # Main directory
        self.__valid_characters: str =  digits + "!#$%&()+[]^{|}" # List of all characters allowed. You can add letters but it is more difficult, the more you add harder it will be.
        self.__space_char: str = "█" # This is the char that will correspond to a space in a sentence.
        self.__messages: List[str] = ["YO HOW ARE YOU ?", 
                                      "NOT GREAT I THINK WE HAVE BEEN COMPROMISED", 
                                      "WAIT SERIOUSLY DAMN THAT SUCKS", 
                                      "LETS KEEP QUIET UNTILL WE HAVE MORE INFO", 
                                      "OKAY", "HEY ITS BEEN 3WEEKS DO YOU HAVE NEWS ?", 
                                      "HEY IT LOOKS LIKE THEY DIDNT FOUND OUR SECRET SO WE ARE GOO !", 
                                      "THAT GREAT NEWS", 
                                      "I WILL SEND YOU WHAT WE TALKED ABOUT IN THE NEXT MESSAGE", 
                                      self.__flag, 
                                      "NICE", 
                                      "DONT FORGET TO DESTROY THE EVIDENCE AFTER"] # Flag goes in here with some other garbage text which must contains only valid characters like up here (space are allowed)
        self.__random_troll: List[str] = ["UlR7WWVhaE5haFRoYXQnc05vdFRoZVJpZ2h0RmxhZ30=", 
                                          "UlR7WWVhaE5haFRoYXQnc05vdFRoZVJpZ2h0RmxhZ30=", 
                                          "UlR7WWVhaE5haFRoYXQnc05vdFRoZVJpZ2h0RmxhZ30=", 
                                          "TG9vc2VyIDopICAgIA==", 
                                          "TG9vc2VyIDopICAgIA==", 
                                          "TG9vc2VyIDopICAgIA==", 
                                          """  ,-.       _,---._ __  / \\
 /  )    .-'       `./ /   \\
(  (   ,'            `/    /|
 \  `-"             \'\   / |
  `.              ,  \ \ /  |
   /`.          ,'-`----Y   |
  (            ;        |   '
  |  ,-.    ,-'         |  /
  |  | (   |            | /
  )  |  \  `.___________|/
  `--'   `--'""",
        """     _______________________________________________________
    /\                                                      \\
(O)===)><><><><><><><><><><><><><><><><><><><><><><><><><><><)==(O)
    \/''''''''''''''''''''''''''''''''''''''''''''''''''''''/
    (                                                      (
     )                                                      )
    (                                                      (
     )                                                      )

    (                                                      (
     )                                                      )
    (                         Looser                       (
     )                                                      )

    (                                                      (
     )                                                      )
    (                                                      (
     )                                                      )

    (                                                      (
     )                                                      )
    (                                                      (
    /\''''''''''''''''''''''''''''''''''''''''''''''''''''''\\
(O)===)><><><><><><><><><><><><><><><><><><><><><><><><><><><)==(O)
    \/______________________________________________________/
        """
                                          ]
        self.__extensions: List[str] = [".txt", ".plist", ".py", ".xml", ".db", ".exe", ".tar", ".zip", ".png", ".jpeg"]

    def main(self):
        """Function that create a directory for each message in self.__messages wich will then create a file for each char in the message.
        It randomly choose the size of the dir/filename and the content of the file too.
        """
        try:
            if not os.path.exists(self.__parent_dir): # Verify if the parent folder is exist
                os.makedirs(self.__parent_dir) # Create the folder if it doesn't exist
                print(f"Creation of {self.__parent_dir} successfully !")

            for index, element in enumerate(self.__messages): # For each message 
                os.makedirs(self.__parent_dir + '/' + str(index)) # And create the directory
                print(f"Creation of {index} successfully !")

                length: int = randint(8,23) # Initialisation of the length for the filename
                pos: int = randint(1, length - 1) # Same for the position of the char in the name
                for num, char in enumerate(element): # For each char we create a file
                    if char == " ": # If there is a space we change it by another char (choosen in the constructor)
                        char = self.__space_char
                    
                    extension: str = ""
                    if random() < 0.2: # Randomly add an extension to the file
                        extension= choice(self.__extensions)
                    
                    # Filename is composed of : Parent_Directory/Index/Random_Filename.extension
                    complete_filename: str = self.__parent_dir + '/' + str(index) + '/'  + self.generate_valid_filename(length, char, pos, num) + extension
                    
                    with open(complete_filename, 'w') as file: # Creation of the file and random content is added
                        content: str
                        if random() > 0.7: # 30% of chance to have a custom content for the file, otherwise it is random
                            content = choice(self.__random_troll)
                        else:
                            content = self.generate_valid_filename(randint(0, 50))
                        file.write(content)
                    print(f"Creation of {complete_filename} successfully !")
            print("Finish !")
        except Exception as e:
            print("Error :", str(e))


    def generate_valid_filename(self, length: int = 10, char: str = '', pos: int = -1, num: int = 0) -> str:
        """Function that create a random filename and add a char inside the filename.

        Args:
            length (int, optional): Length of the filename. Defaults to 10.
            char (str, optional): char that we want to add. Defaults to ''.
            pos (int, optional): Position were the char will be in the filename. Defaults to -1.
            num (int, optional): Id for the file. Defaults to 0.

        Raises:
            IndexError: When the position of the char is outside the length of the filename

        Returns:
            str: Random filename with the char add
        """
        filename: str = ''.join(choices(self.__valid_characters, k=length)) # Random filename

        # Insert of the char
        if pos >= length:
            raise IndexError("L'indice est hors de portée.")
        elif pos > 0:
            filename = filename[:pos] + char + filename[pos+1:]

        filename = f"{num:02d}-{filename}" # Insert of the file number
        return filename

if __name__ == '__main__':
    main = Grabuge()
    main.main()