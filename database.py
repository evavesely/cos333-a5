import sqlite3
from contextlib import closing

DATABASE_URL = "file:reg.sqlite?mode=ro"


def query_database_reg(variables):
    with sqlite3.connect(DATABASE_URL,
                            isolation_level=None,
                            uri=True) as connection:
        with closing(connection.cursor()) as cur:
            # initialize query to be constructed
            # by command line arguments
            query =\
                "SELECT classid, dept, coursenum, area, title " +\
                "FROM courses, crosslistings, classes " +\
                "WHERE courses.courseid=crosslistings.courseid " +\
                "AND courses.courseid=classes.courseid"

            # construct the like statements to refine the search
            like_statements = ""
            for argname in variables.keys():
                like_statements += " AND " + argname + " LIKE ?"
            query += like_statements + ' ESCAPE "\\"'

            # sorting the query: primary is
            query += " ORDER BY dept, coursenum, classid ASC;"
            row = cur.execute(
                query,
                list(variables.values())).fetchone()
            rows = []
            while row is not None:
                rows.append(row)
                row = cur.fetchone()

            return rows


def query_database_regdetails(classid):
    # initialize return datastructure
    rows = {}
    rows['courses'] = {}
    rows['profs'] = []

    # initialize database connection
    # to be closed if error is encounterd
    with sqlite3.connect(DATABASE_URL,
                            isolation_level=None,
                            uri=True) as connection:
        with closing(connection.cursor()) as cur:
            # initialize query to be constructed
            # by command line arguments
            query1 = "SELECT courses.courseid, days," \
                " starttime, endtime, bldg, roomnum," \
                " dept, coursenum, area, title, descrip, prereqs " \
                "FROM courses, crosslistings, classes" \
                " WHERE courses.courseid=crosslistings.courseid " \
                "AND courses.courseid=classes.courseid"
            query2 = "SELECT profname FROM profs, coursesprofs, " \
                "classes WHERE profs.profid=coursesprofs.profid " \
                "AND classes.courseid=coursesprofs.courseid"

            # construct the like statements to refine the search
            like_statements = " AND classid LIKE ?"
            query1 += like_statements
            query2 += like_statements

            # sorting the query: primary is
            query1 += " ORDER BY dept, coursenum ASC;"
            query2 += " ORDER BY profname ASC;"

            row = cur.execute(query1, [classid]).fetchone()
            keys = ["courseid", "days", "start_time",
                    "end_time", "building",
                    "room", "dept", "deptnum",
                    "area", "title", "descrip",
                    "prereq"]

            # if query fails, return nothing
            if row is None:
                return None

            # initialize the data that is constant
            # (that is, not depts)
            depts = [row[6]+" "+row[7]]
            for i, key in enumerate(keys):
                rows['courses'][key] = row[i]

            # then get all the departments
            row = cur.fetchone()
            while row is not None:
                depts.append(row[6]+" "+row[7])
                row = cur.fetchone()
            rows['courses']['depts'] = depts

            # handle multiple professors as a separate query
            row = cur.execute(query2, [classid]).fetchone()
            while row is not None:
                rows['profs'].append(row[0])
                row = cur.fetchone()

            return rows
