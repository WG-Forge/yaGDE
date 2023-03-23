from client.session import Session

if __name__ == "__main__":
    with Session("server:443") as s:
        pass
