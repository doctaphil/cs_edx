import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")

class Node():
    def __init__(self, id, film,parent):
        self.id = id
        self.film = film
        self.parent = parent
        #self.cost = cost

class StackFrontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)
        #print(self.frontier)

    def contains_state(self, id):
        return any(node.id == id for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node
    def getParent(self,id):
        for node in self.frontier:
            if node.id == id:
                return node
    #poging tot printen
    #def __repr__(self):
    #    return f"{type(self).__name__}(value={self.frontier})"
class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors

def find_parents(knoop,source,bronlijst,doellijst):
#functie die vanuit gevonden targetknoop terugloopt tot net voor source en in result lijst brengt
    
        doellijst.append((knoop.film,knoop.id))
             
        while knoop.id!= source:
            knoop = bronlijst.getParent(knoop.parent)
            if knoop.id != source:
                doellijst.append((knoop.film,knoop.id))
                    
        doellijst.reverse()
        #print('gevonden!')
        #print(doellijst)
        return doellijst



def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
        """
    result = []
    
    oorsprong = Node(source,0,0)

    bezocht = QueueFrontier()
    teBezoeken = QueueFrontier()
    # add the first source to visited
    bezocht.add(oorsprong)
    #print(repr(bezocht))
    # https://www.programiz.com/dsa/graph-bfs
    #add all the neighbouring points to the queue = beginvoorwaarde
    buren = neighbors_for_person(source)
    for item in buren:
        knoop = Node(item[1],item[0],source)
        teBezoeken.add(knoop)
        #check of al direct verbonden
        if knoop.id == target:
            result = find_parents(knoop,source,bezocht,result)
            #result.append(knoop.id)
            return result
    #beginvoorwaarden voldaan, nu start zoektocht
    while teBezoeken.empty() != True:
        #visit next neighbouring point(first one in the queue)
        newKnoop = teBezoeken.remove()
        bezocht.add(newKnoop)
            #if target found: return list with points tried (nog te modifieren tot exacte lijst met films en id's)
        if newKnoop.id == target:
            result = find_parents(newKnoop,source,bezocht,result)
            return result
        #check the neighbors of the current point and add any that are not yet in the queue to the back of queue
        buren = neighbors_for_person(newKnoop.id)
        for item in buren:
            newstKnoop = Node(item[1],item[0],newKnoop.id)
            if newstKnoop.id == target:
                result = find_parents(newstKnoop,source,bezocht,result)
                return result
                
            bevatA = teBezoeken.contains_state(newstKnoop.id) 
            bevatB =  bezocht.contains_state(newstKnoop.id)
            if  bevatA == False and bevatB == False:
                teBezoeken.add(newstKnoop)
            
   
    return None    
    # TODO
    #raise NotImplementedError


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]




if __name__ == "__main__":
    main()
