import asyncio

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper, User, Profile, Post
from core.models.order import Order
from core.models.order_product_association import OrderProductAssociation
from core.models.product import Product


# async def create_user(session: AsyncSession, username: str) -> User:
#     user = User(username=username)
#     session.add(user)
#     await session.commit()
#     print("user", user)
#     return user


# async def.scalar_user_by_username(session: AsyncSession, username: str) -> User | None:
#     stmt = select(User).where(User.username == username)
#     # result: Result = await session.execute(stmt)
#     # # user: User | None = result.scalar_one_or_none()
#     # user: User | None = result.scalar_one()
#     user: User | None = await session.scalar(stmt)
#     print("found user", username, user)
#     return user


# async def create_user_profile(
#     session: AsyncSession,
#     user_id: int,
#     first_name: str | None = None,
#     last_name: str | None = None,
# ) -> Profile:
#     profile = Profile(
#         user_id=user_id,
#         first_name=first_name,
#         last_name=last_name,
#     )
#     session.add(profile)
#     await session.commit()
#     return profile


# async def show_users_with_profiles(session: AsyncSession):
#     stmt = select(User).options(joinedload(User.profile)).order_by(User.id)
#     # result: Result = await session.execute(stmt)
#     # users = result.scalars()
#     users = await session.scalars(stmt)
#     for user in users:
#         print(user)
#         print(user.profile.first_name)


# async def create_posts(
#     session: AsyncSession,
#     user_id: int,
#     *posts_titles: str,
# ) -> list[Post]:
#     posts = [Post(title=title, user_id=user_id) for title in posts_titles]
#     session.add_all(posts)
#     await session.commit()
#     print(posts)
#     return posts


# async def.scalar_users_with_posts(
#     session: AsyncSession,
# ):
#     # stmt = select(User).options(joinedload(User.posts)).order_by(User.id)
#     stmt = (
#         select(User)
#         .options(
#             # joinedload(User.posts),
#             selectinload(User.posts),
#         )
#         .order_by(User.id)
#     )
#     # users = await session.scalars(stmt)
#     # result: Result = await session.execute(stmt)
#     # # users = result.unique().scalars()
#     # users = result.scalars()
#     users = await session.scalars(stmt)

#     # for user in users.unique():  # type: User
#     for user in users:  # type: User
#         print("**" * 10)
#         print(user)
#         for post in user.posts:
#             print("-", post)


# async def.scalar_users_with_posts_and_profiles(
#     session: AsyncSession,
# ):
#     stmt = (
#         select(User)
#         .options(
#             joinedload(User.profile),
#             selectinload(User.posts),
#         )
#         .order_by(User.id)
#     )
#     users = await session.scalars(stmt)

#     for user in users:  # type: User
#         print("**" * 10)
#         print(user, user.profile and user.profile.first_name)
#         for post in user.posts:
#             print("-", post)


# async def.scalar_posts_with_authors(session: AsyncSession):
#     stmt = select(Post).options(joinedload(Post.user)).order_by(Post.id)
#     posts = await session.scalars(stmt)

#     for post in posts:  # type: Post
#         print("post", post)
#         print("author", post.user)


# async def.scalar_profiles_with_users_and_users_with_posts(session: AsyncSession):
#     stmt = (
#         select(Profile)
#         .join(Profile.user)
#         .options(
#             joinedload(Profile.user).selectinload(User.posts),
#         )
#         .where(User.username == "john")
#         .order_by(Profile.id)
#     )

#     profiles = await session.scalars(stmt)

#     for profile in profiles:
#         print(profile.first_name, profile.user)
#         print(profile.user.posts)


# async def main_relations(session: AsyncSession):
#     async with db_helper.session_factory() as session:
#         await create_user(session=session, username="john")
#         await create_user(session=session, username="alice")
#         await create_user(session=session, username="sam")
#         user_sam = await.scalar_user_by_username(session=session, username="sam")
#         user_john = await.scalar_user_by_username(session=session, username="john")
#         # user_bob = await.scalar_user_by_username(session=session, username="bob")
#         await create_user_profile(
#             session=session,
#             user_id=user_john.id,
#             first_name="John",
#         )
#         await create_user_profile(
#             session=session,
#             user_id=user_sam.id,
#             first_name="Sam",
#             last_name="White",
#         )
#         await show_users_with_profiles(session=session)
#         await create_posts(
#             session,
#             user_john.id,
#             "SQLA 2.0",
#             "SQLA Joins",
#         )
#         await create_posts(
#             session,
#             user_sam.id,
#             "FastAPI intro",
#             "FastAPI Advanced",
#             "FastAPI more",
#         )
#         await.scalar_users_with_posts(session=session)
#         await.scalar_posts_with_authors(session=session)
#         await.scalar_users_with_posts_and_profiles(session=session)
#         await.scalar_profiles_with_users_and_users_with_posts(session=session)
async def create_orders_and_products(session: AsyncSession):
    order1 = await create_order(session)
    order_promo = await create_order(session, promo_code="promo")
    order2 = await create_order(session)

    # Creăm produsele
    iphone_16 = await create_products(session, "Iphone 16", "Best for photos", 999)
    samsung_s24 = await create_products(
        session, "Samsung S24", "Best for his price", 700
    )

    # Încărcăm relațiile pentru toate comenzile
    order1 = await session.scalar(
        select(Order).where(Order.id == order1.id).options(selectinload(Order.products))
    )
    order_promo = await session.scalar(
        select(Order)
        .where(Order.id == order_promo.id)
        .options(selectinload(Order.products))
    )
    order2 = await session.scalar(  # Adăugăm încărcarea pentru order2
        select(Order).where(Order.id == order2.id).options(selectinload(Order.products))
    )

    # Adăugăm produsele la comenzi
    order1.products.append(samsung_s24)
    order_promo.products.append(samsung_s24)
    order2.products.append(iphone_16)

    await session.commit()


async def get_orders_with_products(session: AsyncSession) -> list[Order]:
    pass


async def create_order(session: AsyncSession, promo_code: str | None = None) -> Order:
    order = Order(promo_code=promo_code)
    session.add(order)
    await session.commit()
    return order


async def create_products(
    session: AsyncSession, name: str, description: str, price: int
) -> Product:
    product = Product(name=name, description=description, price=price)
    session.add(product)
    await session.commit()
    return product


"""
options()---
selectinload()---
joinedload()---
.scalars()---
"""


async def get_orders_with_products_association(session: AsyncSession):
    stmt = (
        select(Order)
        .options(
            selectinload(Order.product_details).joinedload(
                OrderProductAssociation.product
            ),
        )
        .order_by(Order.id)
    )
    orders = await session.scalars(stmt)

    return list(orders)


async def demo_get_orders_with_products_through_secondary(session: AsyncSession):
    # await create_orders_and_products(session)
    orders = await get_orders_with_products(session)
    for order in orders:
        print(f"Order #{order.id}: {order.promo_code} : Created at: {order.created_at}")
        for product in order.products:
            print(f"\tProduct: {product.id} - {product.name} - {product.price}")
        print()


async def demo_get_orders_with_products_with_association(session: AsyncSession):
    orders = await get_orders_with_products_association(session)

    for order in orders:
        print(
            f"Order {order.id}, Promo: {order.promo_code}, Created: {order.created_at}"
        )
        print(f"Number of product details: {len(order.product_details)}")
        for order_product_details in order.product_details:
            print("Product details object:", order_product_details)
            try:
                print(
                    f"Product ID: {order_product_details.product.id if order_product_details.product else 'No product'}, "
                    f"Name: {order_product_details.product.name if order_product_details.product else 'No name'}, "
                    f"Price: {order_product_details.product.price if order_product_details.product else 'No price'}, "
                    f"Quantity: {order_product_details.quantity}"
                )
            except Exception as e:
                print(f"Error accessing product details: {e}")
        print()


# await create_orders_and_products(session)
# orders = await get_orders_with_products_through_secondary(session)
# for order in orders:
#     print(f"Order #{order.id}: {order.promo_code} : Created at: {order.created_at}")
#     for product in order.products:
#         print(f"\tProduct: {product.id} - {product.name} - {product.price}")
#     print()


async def create_gift_product_for_existing_orders(session: AsyncSession):
    orders = await get_orders_with_products_association(session)
    gift_product = await create_products(
        session,
        name="Gift Product",
        description="Gift for you!!",
        price=0,
    )

    for order in orders:
        order.product_details.append(
            OrderProductAssociation(quantity=1, unit_price=0, product=gift_product)
        )
    await session.commit()
    print("Gift product added to orders")


async def demo_many_to_many_relationship(session: AsyncSession):
    await demo_get_orders_with_products_with_association(session)
    # await create_gift_product_for_existing_orders(session)


async def main():
    async with db_helper.session_factory() as session:
        # await main_relations(session)
        await demo_many_to_many_relationship(session)


if __name__ == "__main__":
    asyncio.run(main())
