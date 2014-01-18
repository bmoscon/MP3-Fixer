#!/usr/bin/python3
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

from id3              import ID3
import os
import argparse


class Fixer(object):
    # takes in a directory to operate on
    def __init__(self, d):
        self._files = []
        for dirpath, dirnames, filenames in os.walk(d):
            for filename in filenames:
                if filename.endswith(".mp3"):
                    self._files.append(os.path.join(dirpath, filename))

        self._tags = {f:ID3(f) for f in self._files}


    def __check_track(self, track):
        return track < 0 or track > 31

    def __check_comment(self, comment):
        return len(comment) != 0

    def __check_title(self, title):
        return len(title) == 0

    def __parse_dirs(self, path):
        paths = []
        
        head, tail = os.path.split(path)
        while head:
            paths.append(tail)
            head, tail = os.path.split(head)
        paths.append(tail)
        
        return paths


    def __fix_filename(self, tag, path, base):
        fname = str(tag.track()) + " - " + tag.title() + ".mp3"
        if fname == base:
            return None
        return os.path.join(path, fname)
        
    def fix_files(self):
        for file_name, tag in self._tags.items():
            print("Checking file ", file_name)
            path, base = os.path.split(file_name)
            paths = self.__parse_dirs(path)

            tag.display()

            if self.__check_track(tag.track()):
                print("Incorrect track!")
                track = input("Enter track number: ")
                tag.set_track(track)
            
            if self.__check_comment(tag.comment()):
                tag.set_comment("")
            
            if self.__check_title(tag.title()):
                print("Missing song title!")
                title = input("Enter title: ")
                tag.set_title(title)

            # once all tags are updated the file name can be
            # fixed and made to fit one naming convention
            file_name = self.__fix_filename(tag, path, base)
            
            tag.write_tag(file_name=file_name)





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MP3 Tag Fixer')
    parser.add_argument('--directory', metavar='directory to work in', type=str)
    
    args = parser.parse_args()
    
    if args.directory:
        fixer = Fixer(args.directory)
        fixer.fix_files()
