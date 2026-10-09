import { DataTypes, Model } from "sequelize";

import { sequelize } from "../connection";
import UserSearchSubscription from "./UserSearchSubscription";
import { User as TUser } from "../../types";



class User extends Model<TUser, Omit<TUser, "id">> {
  declare id: number;
  declare username: string;
  declare password: string;
  declare role: string;

  static associate() {
    User.hasMany(
      UserSearchSubscription,
      {
        foreignKey: "user_id",
        as: "subscriptions"
      }
    );
  }
}

User.init(
  {
    id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      allowNull: false,
    },
    username: {
      type: DataTypes.TEXT,
      allowNull: false,
    },
    password: {
      type: DataTypes.TEXT,
      allowNull: false,
    },
    role: {
      type: DataTypes.TEXT,
      allowNull: false,
    },
  },
  {
    sequelize: sequelize,
    freezeTableName: true,
    tableName: "User",
    timestamps: false,
  },
);

export default User;
