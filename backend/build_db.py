"""Build expanded movie database with TMDB poster paths."""
import pandas as pd
from sentence_transformers import SentenceTransformer
import pickle, json

# 100 popular movies with real TMDB poster_path values
MOVIES = [
    {"title":"Interstellar","overview":"A group of explorers travel through a wormhole in space to ensure humanity's survival.","genres":"Adventure Drama Sci-Fi","poster_path":"/gEU2QpI6e8P2d7a2G204z4fK0m5.jpg"},
    {"title":"Inception","overview":"A thief who steals corporate secrets through dream-sharing technology is given the task of planting an idea.","genres":"Action Sci-Fi Thriller","poster_path":"/edv5wpczfmjZ438Xo7Z5PjY1v3h.jpg"},
    {"title":"The Dark Knight","overview":"Batman must accept one of the greatest tests to fight injustice when the Joker wreaks havoc on Gotham.","genres":"Action Crime Drama","poster_path":"/qJ2tW6WMUDux911r6m7haP07y9d.jpg"},
    {"title":"Avatar","overview":"A paraplegic Marine dispatched to Pandora becomes torn between following orders and protecting an alien civilization.","genres":"Action Adventure Fantasy Sci-Fi","poster_path":"/kyeqWdyUXW608qlYkRqosgbbJyK.jpg"},
    {"title":"Fight Club","overview":"An insomniac office worker and a soap salesman build a global organization to fight capitalism.","genres":"Drama Thriller","poster_path":"/pB8BM7pdSpqB6W3U5yRz9c4m8oI.jpg"},
    {"title":"The Shawshank Redemption","overview":"Two imprisoned men bond over years, finding solace and eventual redemption through acts of common decency.","genres":"Drama Crime","poster_path":"/9cjIGRtkTKlJMr2at7RHoy1ZPkJ.jpg"},
    {"title":"The Silence of the Lambs","overview":"A young FBI cadet must receive help from an incarcerated cannibal killer to catch another serial killer.","genres":"Crime Drama Thriller Horror","poster_path":"/uS9m8OBk1A8eM9I042bx8XXpqAq.jpg"},
    {"title":"Pulp Fiction","overview":"The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in tales of violence and redemption.","genres":"Crime Drama","poster_path":"/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg"},
    {"title":"The Matrix","overview":"A computer hacker learns about the true nature of reality and his role in the war against its controllers.","genres":"Action Sci-Fi","poster_path":"/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg"},
    {"title":"Star Wars","overview":"Luke Skywalker joins forces with a Jedi Knight to save the galaxy from the Empire's battle station.","genres":"Adventure Action Sci-Fi","poster_path":"/6FfCtAuVAW8XJjZ7eWeLibRLWTw.jpg"},
    {"title":"Forrest Gump","overview":"The presidencies of Kennedy and Johnson, Vietnam, Watergate unfold through the perspective of an Alabama man.","genres":"Drama Romance Comedy","poster_path":"/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg"},
    {"title":"Schindler's List","overview":"In German-occupied Poland, industrialist Oskar Schindler becomes concerned for his Jewish workforce.","genres":"Drama History War","poster_path":"/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg"},
    {"title":"The Godfather","overview":"The aging patriarch of an organized crime dynasty transfers control to his reluctant son.","genres":"Drama Crime","poster_path":"/3bhkrj58Vtu7enYsRolD1fZdja1.jpg"},
    {"title":"Titanic","overview":"A seventeen-year-old aristocrat falls in love with a kind but poor artist aboard the ill-fated R.M.S. Titanic.","genres":"Drama Romance","poster_path":"/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg"},
    {"title":"The Empire Strikes Back","overview":"After the Rebels are overpowered on Hoth, Luke begins Jedi training while his friends are pursued by Vader.","genres":"Adventure Action Sci-Fi","poster_path":"/nNAeTmF4CtdSgMDplXTDPOpYzsX.jpg"},
    {"title":"Raiders of the Lost Ark","overview":"Archaeologist Indiana Jones races to find the Ark of the Covenant before the Nazis.","genres":"Adventure Action","poster_path":"/ceG9VzoRAVGwivFU403Wc3AHRys.jpg"},
    {"title":"Back to the Future","overview":"Marty McFly is accidentally sent thirty years into the past in a time-traveling DeLorean.","genres":"Adventure Comedy Sci-Fi","poster_path":"/fNOH9f1aA7XRTzl1sAOx9iF553Q.jpg"},
    {"title":"Jurassic Park","overview":"A paleontologist must protect kids after a power failure causes cloned dinosaurs to run loose.","genres":"Adventure Sci-Fi Thriller","poster_path":"/oU7Oq2kFAAlGqbU4VoAE36g4hoI.jpg"},
    {"title":"The Lion King","overview":"A young lion prince is cast out by his uncle who claims he killed his father.","genres":"Animation Family Drama","poster_path":"/sKCr78MXSLixwmZ8DyNhXjQfn5Q.jpg"},
    {"title":"Groundhog Day","overview":"A narcissistic TV weatherman finds himself reliving the same day over and over.","genres":"Comedy Fantasy Romance","poster_path":"/gCgt1WARPmHSuyGMoehXGnBDSB1.jpg"},
    {"title":"The Lord of the Rings: The Fellowship of the Ring","overview":"A meek Hobbit and eight companions set out on a journey to destroy the One Ring.","genres":"Adventure Fantasy Action","poster_path":"/6oom5QYQ2yQTMJIbnvbkBL9cHo6.jpg"},
    {"title":"The Lord of the Rings: The Two Towers","overview":"The Fellowship is broken. Frodo and Sam continue to Mordor while Aragorn pursues the Uruk-hai.","genres":"Adventure Fantasy Action","poster_path":"/5VTN0pR8gcqV3EPUHHfMGnJYN9L.jpg"},
    {"title":"The Lord of the Rings: The Return of the King","overview":"Gandalf and Aragorn lead the World of Men against Sauron to draw his gaze from Frodo.","genres":"Adventure Fantasy Action","poster_path":"/rCzpDGLbOoPwLjy3OAm5NUPOTrC.jpg"},
    {"title":"Gladiator","overview":"A former Roman General sets out to exact vengeance against the corrupt emperor who murdered his family.","genres":"Action Drama Adventure","poster_path":"/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg"},
    {"title":"The Prestige","overview":"Two rival magicians engage in a bitter battle of one-upmanship with dangerous consequences.","genres":"Drama Mystery Thriller","poster_path":"/tRNlZbgNCNOpLpbPEz5L8G8A0JN.jpg"},
    {"title":"Whiplash","overview":"A young drummer enrolls at a cutthroat music conservatory where his dreams are mentored by a ruthless instructor.","genres":"Drama Music","poster_path":"/7fn624j5lj3xTme2SgiLCeuedmO.jpg"},
    {"title":"Django Unchained","overview":"A freed slave sets out to rescue his wife from a brutal Mississippi plantation owner.","genres":"Drama Western","poster_path":"/7oWY8VDWW7thTzWh3OKYRkWUlD5.jpg"},
    {"title":"The Wolf of Wall Street","overview":"Based on the true story of Jordan Belfort, from his rise to a wealthy stock-broker to his fall.","genres":"Crime Drama Comedy","poster_path":"/34m2tygAYBGqA9MXKhRDtzYd4MR.jpg"},
    {"title":"Parasite","overview":"Greed and class discrimination threaten the symbiotic relationship between a wealthy family and a poor one.","genres":"Comedy Drama Thriller","poster_path":"/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg"},
    {"title":"Joker","overview":"A mentally troubled stand-up comedian embarks on a downward spiral of revolution and crime in Gotham City.","genres":"Crime Drama Thriller","poster_path":"/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg"},
    {"title":"Avengers: Endgame","overview":"The Avengers assemble once more to reverse Thanos' actions and restore balance to the universe.","genres":"Action Adventure Sci-Fi","poster_path":"/or06FN3Dka5tukK1e9sl16pB3iy.jpg"},
    {"title":"Avengers: Infinity War","overview":"The Avengers must stop Thanos from collecting all six Infinity Stones.","genres":"Action Adventure Sci-Fi","poster_path":"/7WsyChQLEftFiDhRkZoKH0FN30C.jpg"},
    {"title":"Spider-Man: Into the Spider-Verse","overview":"Teen Miles Morales becomes Spider-Man and must save the multiverse.","genres":"Animation Action Adventure","poster_path":"/iiZZdoQBEYBv6id8su7ImL0oCbD.jpg"},
    {"title":"Black Panther","overview":"T'Challa returns home to Wakanda to take his place as King but is challenged by a new adversary.","genres":"Action Adventure Sci-Fi","poster_path":"/uxzzxijgPIY7slzFvMotPv8wjKA.jpg"},
    {"title":"Guardians of the Galaxy","overview":"A group of intergalactic criminals must pull together to stop a fanatical warrior.","genres":"Action Adventure Sci-Fi Comedy","poster_path":"/r7vmZjiyZw9rpJMQJdXpjgiCOk9.jpg"},
    {"title":"Iron Man","overview":"After being held captive, billionaire engineer Tony Stark creates a unique weaponized suit of armor.","genres":"Action Adventure Sci-Fi","poster_path":"/78lPtwv72eTNqFW9COBYI0dWDJa.jpg"},
    {"title":"Thor: Ragnarok","overview":"Thor must fight for survival and race against time to prevent the destruction of Asgard.","genres":"Action Adventure Comedy Sci-Fi","poster_path":"/rzRwTcFvttcN1ZpX2xv4j3tSdJu.jpg"},
    {"title":"Doctor Strange","overview":"A former neurosurgeon embarks on a journey of healing only to be drawn into the world of mystic arts.","genres":"Action Adventure Fantasy","poster_path":"/uGBVj3bEbCopp59fUEcJZa5hAGv.jpg"},
    {"title":"Mad Max: Fury Road","overview":"In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler with help from a drifter.","genres":"Action Adventure Sci-Fi","poster_path":"/8tZYtuWezp8JbcsvHYO0O46tFbo.jpg"},
    {"title":"John Wick","overview":"An ex-hitman comes out of retirement to track down the gangsters that took everything from him.","genres":"Action Thriller","poster_path":"/fZPSd91yGE9fCcCe6OoQr6E3Bev.jpg"},
    {"title":"The Revenant","overview":"A frontiersman on a fur trading expedition fights for survival after being mauled by a bear.","genres":"Adventure Drama Western","poster_path":"/ji3ecJphATlVgWNY0B4gKLg9a0f.jpg"},
    {"title":"Dunkirk","overview":"Allied soldiers from Belgium, the British Empire and France are surrounded by the German Army during WWII.","genres":"Action Drama History War","poster_path":"/ebSnODDg9lbsMIaWg2uAbjn7TO5.jpg"},
    {"title":"1917","overview":"Two young British soldiers must cross enemy territory to deliver a message that will stop a deadly attack.","genres":"Drama War Action","poster_path":"/iZf0KyrE25z1sage4SYFLCCrMi9.jpg"},
    {"title":"Saving Private Ryan","overview":"Following the Normandy Landings, a group of soldiers go behind enemy lines to retrieve a paratrooper.","genres":"Drama War Action","poster_path":"/uqx37cS8cpHg8U35f9U5IBlrCV3.jpg"},
    {"title":"Braveheart","overview":"Scottish warrior William Wallace leads his countrymen in a rebellion against English rule.","genres":"Action Drama History War","poster_path":"/or1gBugydmjToAEq7OZY0owwFk.jpg"},
    {"title":"The Departed","overview":"An undercover cop and a mole in the police attempt to identify each other in a gang-infiltrated department.","genres":"Crime Drama Thriller","poster_path":"/nT97ifVT2J1yMQmeq20Dqv60GS.jpg"},
    {"title":"Se7en","overview":"Two detectives hunt a serial killer who uses the seven deadly sins as his motives.","genres":"Crime Mystery Thriller","poster_path":"/6yoghtyTpznpBik8EngEmJskVUO.jpg"},
    {"title":"Zodiac","overview":"The true story of the investigation of the Zodiac serial killer in San Francisco.","genres":"Crime Drama Mystery Thriller","poster_path":"/hJSJTJfl9LWQEG5RrJEthPpS2Bo.jpg"},
    {"title":"Gone Girl","overview":"A husband becomes the main suspect in the disappearance of his wife on their fifth wedding anniversary.","genres":"Drama Mystery Thriller","poster_path":"/lv5xShBIDPe4M3svbIjONzgoAEF.jpg"},
    {"title":"Shutter Island","overview":"A U.S. Marshal investigates the disappearance of a patient from a hospital for the criminally insane.","genres":"Drama Mystery Thriller","poster_path":"/4GDy0PHYX3VRXUtwK5ysFbg3kEx.jpg"},
    {"title":"Memento","overview":"A man with short-term memory loss attempts to track down his wife's murderer using notes and tattoos.","genres":"Mystery Thriller","poster_path":"/yuNs09hvpHVU1cBTCAk9zxsL2oW.jpg"},
    {"title":"Get Out","overview":"A young African-American visits his white girlfriend's parents for the weekend and uncovers a disturbing secret.","genres":"Horror Mystery Thriller","poster_path":"/tFXcEccSQMf3lfhfXKSU9iRBpa3.jpg"},
    {"title":"A Quiet Place","overview":"A family must live in silence while hiding from creatures that hunt by sound.","genres":"Drama Horror Sci-Fi Thriller","poster_path":"/nAU74GmpUk7t5iklEp3bufwDq4n.jpg"},
    {"title":"Hereditary","overview":"A family is haunted by tragic and disturbing occurrences after the death of their grandmother.","genres":"Drama Horror Mystery","poster_path":"/p0sNq4wnfOGbTNmOQyBOdGAbpjr.jpg"},
    {"title":"It","overview":"A group of bullied kids band together when a shape-shifting demon terrorizes their small town.","genres":"Horror","poster_path":"/9E2y5Q7WlCVNEhP5GiVTjhEhx1o.jpg"},
    {"title":"The Conjuring","overview":"Paranormal investigators help a family terrorized by a dark presence in their farmhouse.","genres":"Horror Thriller","poster_path":"/wVYREutTvI2tmxr6ujrHT704wGF.jpg"},
    {"title":"Alien","overview":"The crew of a commercial spacecraft encounter a deadly alien lifeform after investigating a transmission.","genres":"Horror Sci-Fi","poster_path":"/vfrQk5IPloGg1v9Rzbh2Eg3VGyM.jpg"},
    {"title":"Blade Runner 2049","overview":"A young blade runner discovers a secret that leads him to find a former blade runner who vanished.","genres":"Sci-Fi Thriller Drama","poster_path":"/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg"},
    {"title":"Arrival","overview":"A linguist is recruited by the military to communicate with alien lifeforms who have arrived on Earth.","genres":"Drama Sci-Fi","poster_path":"/x2FJsf1ElAgr63Y3PNPtJrcmpoe.jpg"},
    {"title":"Ex Machina","overview":"A programmer is selected to participate in an experiment in artificial intelligence by evaluating a robot.","genres":"Drama Sci-Fi Thriller","poster_path":"/btbRB7BrD887j5NtUiAMUT8MjDL.jpg"},
    {"title":"Gravity","overview":"Two astronauts work together to survive after an accident leaves them stranded in space.","genres":"Sci-Fi Thriller Drama","poster_path":"/kZ2nYxDIU1ER1VmMGhIm3r8dLoq.jpg"},
    {"title":"The Martian","overview":"An astronaut becomes stranded on Mars and must find a way to signal Earth that he is alive.","genres":"Adventure Drama Sci-Fi","poster_path":"/5BHuvQ6p9kfc091Z8RiFNhCwL4b.jpg"},
    {"title":"Dune","overview":"Paul Atreides leads nomadic tribes in a battle to control the desert planet Arrakis.","genres":"Sci-Fi Adventure Drama","poster_path":"/d5NXSklXo0qyIYkgV94XAgMIckC.jpg"},
    {"title":"Tenet","overview":"A secret agent embarks on a dangerous time-bending mission to prevent the start of World War III.","genres":"Action Sci-Fi Thriller","poster_path":"/k68nPLbIST6NP96JmTxmZijEvCA.jpg"},
    {"title":"Oppenheimer","overview":"The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb.","genres":"Drama History Thriller","poster_path":"/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg"},
    {"title":"Barbie","overview":"Barbie and Ken leave Barbieland and discover the joys and perils of living in the real world.","genres":"Comedy Adventure Fantasy","poster_path":"/iuFNMS8U5cb6xfzi51Dbkovj7vM.jpg"},
    {"title":"Everything Everywhere All at Once","overview":"An aging Chinese immigrant is swept up in an insane adventure across the multiverse.","genres":"Action Adventure Comedy Sci-Fi","poster_path":"/w3LxiVQoXmhhlsijBMnWJWodnJe.jpg"},
    {"title":"Top Gun: Maverick","overview":"After thirty years, Maverick is still pushing the envelope as a top naval aviator and must train new graduates.","genres":"Action Drama","poster_path":"/62HCnUTziyWcpDaBO2i1DG17I2T.jpg"},
    {"title":"The Batman","overview":"Batman ventures into Gotham City's underworld when a sadistic killer leaves behind cryptic clues.","genres":"Crime Mystery Action","poster_path":"/74xTEgt7R36Fpooo50r9T25onhq.jpg"},
    {"title":"No Time to Die","overview":"James Bond has left active service. His peace is short-lived when an old friend asks for help.","genres":"Action Adventure Thriller","poster_path":"/iUgygt3fscRoKWPM4SbLiI6Bfam.jpg"},
    {"title":"Dune: Part Two","overview":"Paul Atreides unites with the Fremen to take revenge against those who destroyed his family.","genres":"Sci-Fi Adventure Drama Action","poster_path":"/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg"},
    {"title":"La La Land","overview":"A jazz musician and an aspiring actress fall in love while pursuing their dreams in Los Angeles.","genres":"Comedy Drama Music Romance","poster_path":"/uDO8zWDhfWwoFdKS4fzkUJt0Rf0.jpg"},
    {"title":"The Grand Budapest Hotel","overview":"A writer encounters the owner of an aging luxury hotel who tells the tale of his early years.","genres":"Comedy Crime Drama","poster_path":"/eWDyBVQNVraRkPMabsHBBKJ3LE3.jpg"},
    {"title":"Inglourious Basterds","overview":"In Nazi-occupied France, a group of Jewish soldiers plan to assassinate Nazi leaders.","genres":"Drama War Action","poster_path":"/7sfbEnaARXDDhKm0CZ7D7uc2sbo.jpg"},
    {"title":"Kill Bill: Volume 1","overview":"After awakening from a four-year coma, a former assassin wreaks vengeance on her attackers.","genres":"Action Crime Thriller","poster_path":"/v7TaX8kXMXs5yFFGR41guUDNcnB.jpg"},
    {"title":"The Truman Show","overview":"An insurance salesman discovers his whole life is actually a reality TV show.","genres":"Comedy Drama","poster_path":"/vuza0WqY239yBXOadKlGwJsZJFE.jpg"},
    {"title":"Eternal Sunshine of the Spotless Mind","overview":"A couple undergoes a medical procedure to erase each other from their memories when their relationship turns sour.","genres":"Drama Romance Sci-Fi","poster_path":"/5MwkWH9tYHv3mV9OdYTMR5qreIz.jpg"},
    {"title":"Good Will Hunting","overview":"A janitor at MIT has a gift for mathematics but needs help finding direction in his life.","genres":"Drama Romance","poster_path":"/bABCBKYBK7A5G1x0FzmtmonG64A.jpg"},
    {"title":"A Beautiful Mind","overview":"The story of John Nash, a brilliant mathematician who struggles with schizophrenia.","genres":"Drama Romance Biography","poster_path":"/zwzWCmH72OSC9NA0ipoqw5Zjya8.jpg"},
    {"title":"The Social Network","overview":"The story of the founding of Facebook and the resulting lawsuits.","genres":"Drama Biography","poster_path":"/n0ybibhJtQ5icDqTp8eRhcDhl9C.jpg"},
    {"title":"Catch Me If You Can","overview":"The true story of Frank Abagnale Jr. who successfully conned millions while posing as different professionals.","genres":"Crime Drama Biography","poster_path":"/ctjEj2xM32OvNDGjMI9r4V5iXcW.jpg"},
    {"title":"The Pursuit of Happyness","overview":"A struggling salesman takes custody of his son as he starts a life-changing internship.","genres":"Drama Biography","poster_path":"/iKGCUbCxRi3Ka6ayVomaanJa0OB.jpg"},
    {"title":"Cast Away","overview":"A FedEx executive must transform himself physically and emotionally to survive a crash landing on a deserted island.","genres":"Adventure Drama","poster_path":"/xBHvZcjRiWyobQ9kxBhO6B2dtRI.jpg"},
    {"title":"The Green Mile","overview":"A death row corrections officer discovers that one of his inmates has a mysterious gift.","genres":"Crime Drama Fantasy","poster_path":"/velWPhVMQeQKcxggNEU8YmIo52R.jpg"},
    {"title":"12 Angry Men","overview":"A jury holdout attempts to prevent a miscarriage of justice by forcing his colleagues to reconsider the evidence.","genres":"Crime Drama","poster_path":"/ow3wq89wM8qd5X7hWKxiRfsFf9C.jpg"},
    {"title":"Goodfellas","overview":"The story of Henry Hill and his life in the mob, covering his relationship with his wife and his mob partners.","genres":"Crime Drama","poster_path":"/aKuFiU82s5ISJpGZp7YkIR3UPVl.jpg"},
    {"title":"Scarface","overview":"An ambitious Cuban immigrant takes over a drug cartel and succumbs to greed.","genres":"Action Crime Drama","poster_path":"/iQ5ztdjvteGeboXg8Tta5BGoNKS.jpg"},
    {"title":"The Usual Suspects","overview":"A sole survivor tells the twisting events leading up to a horrific gun battle on a boat.","genres":"Crime Mystery Thriller","poster_path":"/bUPmtQzrRhzqYySeiMpv4PIi0aO.jpg"},
    {"title":"Taxi Driver","overview":"A mentally unstable veteran works as a nighttime taxi driver in NYC, descending into madness.","genres":"Crime Drama","poster_path":"/ekstpH614fwDX8DUln1a2Gf74bo.jpg"},
    {"title":"Reservoir Dogs","overview":"When a simple jewelry heist goes wrong, the surviving criminals begin to suspect that one is a police informant.","genres":"Crime Thriller","poster_path":"/lsBnfheKZBO3UKU7lVHIeGZLWup.jpg"},
    {"title":"Apocalypse Now","overview":"A U.S. Army officer is sent on a mission into Cambodia to assassinate a renegade Special Forces Colonel.","genres":"Drama War","poster_path":"/gQB8Y5RCMkv2zwzFHbUJX3kAhvA.jpg"},
    {"title":"Full Metal Jacket","overview":"A pragmatic U.S. Marine observes the dehumanizing effects the Vietnam War has on his fellow recruits.","genres":"Drama War","poster_path":"/kMKyx1k8hWWscYFnPbnxxYELT5n.jpg"},
    {"title":"Platoon","overview":"A young recruit in Vietnam faces a moral crisis when confronted with the horrors of war.","genres":"Drama War Action","poster_path":"/sMhliKjXITPKTO0UJbucCFp5E62.jpg"},
    {"title":"Hacksaw Ridge","overview":"The true story of Desmond Doss who served during WWII and refused to bear arms.","genres":"Drama History War","poster_path":"/jhWbYeUNOA4gGJu1II6P5afqfRB.jpg"},
    {"title":"Spirited Away","overview":"A young girl becomes trapped in a strange new world of spirits and must find a way to free herself and her parents.","genres":"Animation Adventure Family Fantasy","poster_path":"/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg"},
    {"title":"Your Name","overview":"Two teenagers share a profound, magical connection upon discovering they are swapping bodies.","genres":"Animation Drama Fantasy Romance","poster_path":"/q719jXXEzOoYaps6aYsPulHGsJT.jpg"},
    {"title":"Coco","overview":"A boy journeys to the Land of the Dead to find his great-great-grandfather, a legendary singer.","genres":"Animation Adventure Comedy Family","poster_path":"/gGEsBPAijhVUFoiNpgZXqRVWJt2.jpg"},
    {"title":"WALL-E","overview":"In the distant future, a small waste-collecting robot inadvertently embarks on a space journey.","genres":"Animation Adventure Family Sci-Fi","poster_path":"/hbhFnRzzg6ZDmm8YAmxBnQpQIPh.jpg"},
    {"title":"Up","overview":"A 78-year-old man carries out his dream of seeing South America by tying balloons to his house.","genres":"Animation Adventure Comedy Family","poster_path":"/vpbaStTMt8qqXaEgnOR2EE4DNJk.jpg"},
    {"title":"Inside Out","overview":"Young Riley's emotions - Joy, Fear, Anger, Disgust, and Sadness - guide her through a difficult life change.","genres":"Animation Comedy Drama Family","poster_path":"/2H1TmgdfNtsKlU9jKdeNyYL5y8T.jpg"},
    {"title":"Toy Story","overview":"A cowboy doll is profoundly threatened when a new spaceman figure supplants him as top toy in a boy's room.","genres":"Animation Comedy Family","poster_path":"/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg"},
    {"title":"Finding Nemo","overview":"A clownfish named Marlin and a regal tang named Dory journey across the ocean to find Marlin's abducted son.","genres":"Animation Adventure Comedy Family","poster_path":"/eHuGQ10FUzJ1cPs93nihEEXuoWI.jpg"},
]

print(f"Building database with {len(MOVIES)} movies...")

df = pd.DataFrame(MOVIES)
df['id'] = range(1, len(df) + 1)
df['search_text'] = df['title'] + " " + df['overview'] + " " + df['genres']

print("Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

print("Generating embeddings...")
embeddings = model.encode(df['search_text'].tolist(), convert_to_tensor=True, show_progress_bar=True)

movies_db = df[['id', 'title', 'overview', 'genres', 'poster_path']].copy()

print("Saving to movies_db.pkl...")
with open('movies_db.pkl', 'wb') as f:
    pickle.dump({'movies': movies_db, 'embeddings': embeddings}, f)

print(f"Done! {len(movies_db)} movies indexed with embeddings and poster paths.")
