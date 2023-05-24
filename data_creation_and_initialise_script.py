import pandas as pd
import sqlite3
from sklearn.metrics.pairwise import cosine_similarity


def save_csv_data(file_name, table_name):
    df = pd.read_csv(
        file_name, encoding="ISO-8859–1", delimiter=";", on_bad_lines="skip"
    )
    df.columns = [x.lower().replace("-", "_") for x in df.columns.tolist()]
    conn = sqlite3.connect("database/bookrecommender.sqllite")
    query = f'Create table if not Exists {table_name} ({",".join(df.columns.tolist())})'
    print("*********", query)
    conn.execute(query)
    df.to_sql(table_name, conn, if_exists="replace", index=True)
    conn.commit()
    conn.close()


def save_item_item():
    ratings = pd.read_csv("BX-Book-Ratings.csv", encoding="ISO-8859–1", delimiter=";")
    ratings = ratings.rename(
        columns={"User-ID": "user_id", "ISBN": "isbn", "Book-Rating": "book_rating"}
    )
    ratings["user_id"] = ratings["user_id"].astype(str)
    ratings["isbn"] = ratings["isbn"].astype(str)
    ratings["book_rating"] = ratings["book_rating"].astype(int)

    ratings_grp = ratings.groupby(by="isbn", as_index=False).count()
    ratings_grp = ratings_grp.loc[ratings_grp.user_id > 10, :]
    ratings = ratings.loc[ratings.isbn.isin(ratings_grp["isbn"]), :]
    print(f"******** rating 1 : {len(ratings)}")

    ratings_grp2 = ratings.groupby(by="user_id", as_index=False).count()
    ratings_grp2 = ratings_grp2.loc[ratings_grp2.isbn > 10, :]
    ratings = ratings.loc[ratings.user_id.isin(ratings_grp2["user_id"]), :]
    print(f"******** rating 1 : {len(ratings)}")

    pt = ratings.pivot_table(
        index="isbn", columns="user_id", values="book_rating"
    ).fillna(0)

    cosin_simi = cosine_similarity(pt)

    simi_matrix = pd.DataFrame(
        cosin_simi, columns=pt.index.tolist(), index=pt.index.tolist()
    )
    item_item_matrix = pd.DataFrame(
        simi_matrix.unstack(), columns=["rating"]
    ).reset_index()
    item_item_matrix.columns = ["isbn1", "isbn2", "rating"]

    conn = sqlite3.connect("database/bookrecommender.sqllite")
    query = f'Create table if not Exists item_iteam_matrix ({",".join(item_item_matrix.columns.tolist())})'
    print("*********", query)
    conn.execute(query)
    item_item_matrix.to_sql("item_iteam_matrix", conn, if_exists="replace", index=True)
    conn.commit()
    conn.close()


def initialise():
    for file_name in [
        ("BX-Book-Ratings.csv", "ratings"),
        ("BX-Books_small.csv", "books"),
        ("BX-Users.csv", "users"),
    ]:
        save_csv_data(file_name[0], file_name[1])
    save_item_item()


if __name__ == "__main__":
    initialise()
