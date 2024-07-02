from dataclasses import dataclass


@dataclass
class UserService: ...


# session_maker: AsyncSessionMaker
# async def create(user: User):
#     async with session_maker() as session:
#         user_repo = UserRepository(session)
