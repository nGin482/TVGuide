// id: Mapped[int] = Column('id', Integer, primary_key=True, autoincrement=True)
// user_id: Mapped[int] = Column('user_id', Integer, ForeignKey('User.id'))
// search_id: Mapped[int] = Column('search_id', Integer, ForeignKey('SearchItem.id'))

import { DataTypes, Model } from "sequelize";

import { sequelize } from "../connection";
import User from "./User";
import SearchItem from "./SearchItem";
import { UserSearchSubscription as Subscription } from "../../types";



class UserSearchSubscription extends Model<Subscription, Omit<Subscription, "id">> {
  declare id: number;
  declare userId: number;
  declare searchId: number;

  static associate() {
    UserSearchSubscription.belongsTo(
      User,
      {
        foreignKey: "user_id",
        as: "subscriptions"
      }
    );
    UserSearchSubscription.belongsTo(
      SearchItem,
      {
        foreignKey: "search_id"
      }
    )
  }
}

UserSearchSubscription.init(
  {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      allowNull: false,
    },
    userId: {
      type: DataTypes.INTEGER,
      allowNull: false,
      field: "user_id",
    },
    searchId: {
      type: DataTypes.INTEGER,
      allowNull: false,
      field: "search_id",
    },
  },
  {
    sequelize: sequelize,
    freezeTableName: true,
    tableName: "UserSearchSubscription",
    timestamps: false,
  },
);

export default UserSearchSubscription;
