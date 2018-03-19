# from typing import bool
import sqlite3
import os
from w3z_app import core

dir_path = os.path.dirname(os.path.abspath(__file__))


class DB:
    def _get_conn(self):
        return sqlite3.connect(os.path.join(dir_path, '../w3p.db'))

    def set_link(self, url: str, slug: str, isprivate: bool):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT LinkID from LinkList where url=?", (url,))
        data = cursor.fetchone()
        if data is None:
            cursor.execute("Insert into LinkList(LinkID, url) values(?,?)", (None,url))
            conn.commit()
            cursor.execute("SELECT LinkID from LinkList where url=?", (url,))
            data = cursor.fetchone()
        linkid = data[0]
        if isprivate is True:
            return self.createprivate(linkid, slug, isprivate)
        else:
            return self.createpublic(linkid, slug, isprivate)

    def get_link(self, slug, isprivate):
        if slug is None:
            return None
        print(slug)
        conn = self._get_conn()
        cursor = conn.cursor()
        if isprivate is False:
            cursor.execute("""select ConvertedUrl from PublicLinks where 
                                    LinkID in(select LinkID from LinkList where url = ?)""", (slug,))
            data = cursor.fetchone()
            conn.close()
            return data[0] if data else None
        elif isprivate is True:
            cursor.execute(
                "Select ConvertedUrl from PrivateLinks where ConvertedUrl = ?", (slug,))
            data = cursor.fetchone()
            conn.close()
            return data[0] if data else None
        else:
            exporturl = None        # Initialize
            print("fetch url")
            cursor.execute(
                "Select LinkID from PrivateLinks where ConvertedUrl = ?", (slug,))
            data = cursor.fetchone()
            print(data)
            if data is not None:
                linkid = data[0]
                print("got from private")
                cursor.execute("Select url from LinkList where LinkID = ?", (linkid,))
                linkdata = cursor.fetchone()
                exporturl = linkdata[0]
            else:
                cursor.execute(
                "Select LinkID from PublicLinks where ConvertedUrl = ?", (slug,))
                data = cursor.fetchone()
                print(data)
                if data is not None:
                    linkid = data[0]
                    print("got from public")
                    cursor.execute("Select url from LinkList where LinkID = ?", (linkid,))
                    linkdata = cursor.fetchone()
                    exporturl = linkdata[0]
            conn.close()
            return exporturl

    def createprivate(self, linkid, slug, isprivate):
        conn = self._get_conn()
        cursor = conn.cursor()
        if self.checkexisting(isprivate, slug) is None:
            if self.checkexisting(not isprivate, slug) is None:
                cursor.execute(
                    "INSERT INTO PrivateLinks VALUES(?, ?)", (slug, linkid))
                conn.commit()
                conn.close()
                return True
            else:
                conn.close()
                return False
        else:
            conn.close()
            return False

    def createpublic(self, linkid, slug, isprivate):
        conn = self._get_conn()
        cursor = conn.cursor()
        if self.checkexisting(isprivate, slug) is None:
            if self.checkexisting(not isprivate, slug) is None:
                cursor.execute(
                    "INSERT INTO PublicLinks VALUES(?, ?)", (linkid, slug))
                conn.commit()
        conn.close()
        return True

    def checkexisting(self, isprivate, shorturl):
        conn = self._get_conn()
        cursor = conn.cursor()
        table = "PrivateLinks" if isprivate else "PublicLinks"
        cursor.execute("SELECT * from " + table + " where ConvertedUrl = ?", (shorturl,))
        data = cursor.fetchone()
        conn.close()
        return data
