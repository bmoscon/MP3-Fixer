'''
Copyright (C) 2013-2014  Bryant Moscon - bmoscon@gmail.com
 
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to 
 deal in the Software without restriction, including without limitation the 
 rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 sell copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 1. Redistributions of source code must retain the above copyright notice, 
    this list of conditions, and the following disclaimer.

 2. Redistributions in binary form must reproduce the above copyright notice, 
    this list of conditions and the following disclaimer in the documentation 
    and/or other materials provided with the distribution, and in the same 
    place and form as other copyright, license and disclaimer information.

 3. The end-user documentation included with the redistribution, if any, must 
    include the following acknowledgment: "This product includes software 
    developed by Bryant Moscon (http://www.bryantmoscon.org/)", in the same 
    place and form as other third-party acknowledgments. Alternately, this 
    acknowledgment may appear in the software itself, in the same form and 
    location as other such third-party acknowledgments.

 4. Except as contained in this notice, the name of the author, Bryant Moscon,
    shall not be used in advertising or otherwise to promote the sale, use or 
    other dealings in this Software without prior written authorization from 
    the author.


 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
 THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN 
 THE SOFTWARE.
'''


import struct
import shutil
import os

class Tag(object):
    def __init__(self, title, artist, album, year, comment, track, genre):
        self.title = title
        self.artist = artist
        self.album = album
        self.year = year
        self.comment = comment
        self.track = track
        self.genre = genre


    def to_bytes(self):
        byte_data = b"TAG"
        byte_data += self.title.encode('UTF-8') + (b"\x00" * (30 - len(self.title)))
        byte_data += self.artist.encode('UTF-8') + (b"\x00" * (30 - len(self.artist)))
        byte_data += self.album.encode('UTF-8') + (b"\x00" * (30 - len(self.album)))

        if self.year:
            byte_data += self.year.encode('UTF-8')
        else:
            byte_data += b"\x00\x00\x00\x00"

        byte_data += self.comment.encode('UTF-8') + (b"\x00" * (29 - len(self.comment)))
        byte_data += bytes([int(self.track)])
        byte_data += bytes([self.genre])

        return byte_data


class ID3(object):
    TAG_ID3v1  = 1
    TAG_ID3v2  = 2

    GENRES = [
        "Blues",
        "Classic Rock",
        "Country",
        "Dance",
        "Disco",
        "Funk",
        "Grunge",
        "Hip-Hop",
        "Jazz",
        "Metal",
        "New Age",
        "Oldies",
        "Other",
        "Pop",
        "R&B",
        "Rap",
        "Reggae",
        "Rock",
        "Techno",
        "Industrial",
        "Alternative",
        "Ska",
        "Death Metal",
        "Pranks",
        "Soundtrack",
        "Euro-Techno",
        "Ambient",
        "Trip-Hop",
        "Vocal",
        "Jazz+Funk",
        "Fusion",
        "Trance",
        "Classical",
        "Instrumental",
        "Acid",
        "House",
        "Game",
        "Sound Clip",
        "Gospel",
        "Noise",
        "Alt. Rock",
        "Bass",
        "Soul",
        "Punk",
        "Space",
        "Meditative",
        "Instrumental Pop",
        "Instrumental Rock",
        "Ethnic",
        "Gothic",
        "Darkwave",
        "Techno-Industrial",
        "Electronic",
        "Pop-Folk",
        "Eurodance",
        "Dream",
        "Southern Rock",
        "Comedy",
        "Cult",
        "Gangsta Rap",
        "Top 40",
        "Christian Rap",
        "Pop/Funk",
        "Jungle",
        "Native American",
        "Cabaret",
        "New Wave",
        "Psychedelic",
        "Rave",
        "Showtunes",
        "Trailer",
        "Lo-Fi",
        "Tribal",
        "Acid Punk",
        "Acid Jazz",
        "Polka",
        "Retro",
        "Musical",
        "Rock & Roll",
        "Hard Rock",
        "Folk",
        "Folk-Rock",
        "National Folk",
        "Swing",
        "Fast Fusion",
        "Bebop",
        "Latin",
        "Revival",
        "Celtic",
        "Bluegrass",
        "Avantgarde",
        "Gothic Rock",
        "Progressive Rock",
        "Psychedelic Rock",
        "Symphonic Rock",
        "Slow Rock",
        "Big Band",
        "Chorus",
        "Easy Listening",
        "Acoustic",
        "Humour",
        "Speech",
        "Chanson",
        "Opera",
        "Chamber Music",
        "Sonata",
        "Symphony",
        "Booty Bass",
        "Primus",
        "Porn Groove",
        "Satire",
        "Slow Jam",
        "Club",
        "Tango",
        "Samba",
        "Folklore",
        "Ballad",
        "Power Ballad",
        "Rhythmic Soul",
        "Freestyle",
        "Duet",
        "Punk Rock",
        "Drum Solo",
        "A Cappella",
        "Euro-House",
        "Dance Hall",
        "Goa",
        "Drum & Bass",
        "Club-House",
        "Hardcore",
        "Terror",
        "Indie",
        "BritPop",
        "Negerpunk",
        "Polsk Punk",
        "Beat",
        "Christian Gangsta Rap",
        "Heavy Metal",
        "Black Metal",
        "Crossover",
        "Contemporary Christian",
        "Christian Rock",
        "Merengue",
        "Salsa",
        "Thrash Metal",
        "Anime",
        "JPop",
    ]

    def __init__(self, file_name):
        self.file_name = file_name
        self.tag_type = self.__classify()
        self.fields = self.__populate()
        self.modified = False
        
          
    def __classify(self):
        with open(self.file_name, "rb") as fp:
            # Check for ID3V1 
            fp.seek(-128, 2)
            # Header size is 3 bytes
            header = fp.read(3)

            try:    
                header = header.decode('UTF-8')
            except:
                pass
            
            if header == 'TAG':
                return self.TAG_ID3v1
                
            else:
                # Check for ID3v2
                fp.seek(0, 0)
                header = fp.read(10)
                try:
                    header = header.decode('UTF-8', 'ignore')
                except:
                    pass
                    
                if header == 'ID3':
                    return self.TAG_ID3v2
                else:
                    return None
    
    def __populate(self):
        fields = None
        if self.tag_type == self.TAG_ID3v1:
            v1_fmt = "30s30s30s4s29s"
            with open(self.file_name, mode='rb') as fp:
                fp.seek(-125, 2)
                line = fp.read(123)
                args = tuple((lambda s: s.decode('UTF-8', 'ignore').replace("\x00", ""))(s) for s in struct.unpack(v1_fmt, line))
                args += struct.unpack("BB", fp.read(2))
                fields = Tag(*args)
        return fields


    def write_tag(self, file_name=None, backup=True):
        # if we havent changed the fields in the tag
        # and we havent updated the file name, then there
        # isnt anything to do
        if self.modified == False and file_name is None:
            return

        id3_tag = self.fields.to_bytes()
        
        if len(id3_tag) != 128:
            print("ERROR converting ID3 tag to byte array for writing!")
            return
            
        # make a backup before writing the file, just in case!
        if backup:
            shutil.copy2(self.file_name, self.file_name+'.bak')

        # in case we've updated the file name
        if file_name:
            shutil.copy2(self.file_name, file_name)
            os.remove(self.file_name)
            self.file_name = file_name
            

        with open(self.file_name, mode='r+b') as fp:
            fp.seek(-128, 2)
            fp.write(id3_tag)


    def track(self):
        return self.fields.track

    def set_track(self, t):
        self.fields.track = t
        self.modified = True

    def comment(self):
        return self.fields.comment

    def set_comment(self, c):
        self.fields.comment = c
        self.modified = True

    def title(self):
        return self.fields.title

    def set_title(self, t):
        self.fields.title = t
        self.modified = True

    def album(self):
        return self.fields.album

    def set_album(self, a):
        self.fields.album = a

    def artist(self):
        return self.fields.artist

    def set_artist(self, a):
        self.fields.artist = a

    def year(self):
        return self.fields.year

    def set_year(self, y):
        self.fields.year = y

    def genre(self):
        return self.fields.genre

    def set_genre(self, g):
        self.fields.genre = g


    def display(self):
        if self.tag_type == self.TAG_ID3v1:
            print("Title:   ", self.fields.title)
            print("Artist:  ", self.fields.artist)
            print("Album:   ", self.fields.album)
            print("Track:   ", self.fields.track)
            print("Year:    ", self.fields.year)
            print("Genre:   ", self.GENRES[self.fields.genre])
            print("Comment: ", self.fields.comment)
            print()

