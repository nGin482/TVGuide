import { useContext, useEffect, useState } from "react";
import { useParams } from "react-router";
import { Helmet } from "react-helmet";
import { Alert, App, Button, List, Space, Spin, Typography } from "antd";

import TVGuide from "../components/TVGuide";
import { SubscriptionForm } from "../components/SubscriptionForm";
import { UserContext } from "../contexts/UserContext";
import {
    addSubscriptions,
    getGuide,
    getUser,
    getUserSubscriptions,
    unsubscribeFromSearch
} from "../requests";
import { sessionExpiryMessage } from "../utils";
import { Guide, SubscriptionsPayload, SubscriptionsAction, User } from "../utils/types";
import "../styles/ProfilePage.css";

interface UserParam {
    user: string
}

const ProfilePage = () => {
    const { user } = useParams<UserParam>();
    const { currentUser, setUser } = useContext(UserContext);
    
    const [viewingOwnProfile, setViewingOwnProfile] = useState(false);
    const [userDetails, setUserDetails] = useState<User>(null);
    const [loadingUser, setLoadingUser] = useState(false);
    const [userTVGuide, setUserTVGuide] = useState<Guide>(null);
    const [showSubscriptionModal, setShowSubscriptionModal] = useState(false);
    
    const { notification } = App.useApp();
    const { Text } = Typography;
    
    useEffect(() => {
        if (user) {
            setLoadingUser(true);
            fetchUser(user);
            fetchUserSubscriptions(user);
            fetchGuide();
        }
    }, [user]);

    useEffect(() => {
        if (user && currentUser && user === currentUser.username) {
            setViewingOwnProfile(true);
        }
    }, [user, currentUser]);

    const fetchUser = async (username: string) => {
        const user = await getUser(username);
        setUserDetails(user);
        setLoadingUser(false);
    };

    const fetchUserSubscriptions = async (username: string) => {
        await getUserSubscriptions(username);
    };

    const fetchGuide = async () => {
        const guide = await getGuide();
        setUserTVGuide(guide);
    };

    const toggleModal = () => {
        setShowSubscriptionModal(current => !current);
    };

    const unsubscribe = async (subscriptionId: number) => {
        const payload: SubscriptionsPayload = {
            unsubscribe: {
                subscriptionId
            }
        };
        updateSubscriptionsHandle(payload, "unsubscribe");
    };

    const updateSubscriptionsHandle = async (
        subscriptionsPayload: SubscriptionsPayload,
        action: SubscriptionsAction
    ) => {
        try {
            let updatedUserDetails: User;
            if (action === "unsubscribe") {
                const subscriptionId = subscriptionsPayload.unsubscribe.subscriptionId;
                await unsubscribeFromSearch(subscriptionId, currentUser.token);
                updatedUserDetails = {
                    ...userDetails,
                    show_subscriptions: userDetails.show_subscriptions.filter(
                        subscription => subscription.id !== subscriptionId
                    )
                };
            }
            else {
                const subscriptions = subscriptionsPayload.subscribe.show_subscriptions;
                updatedUserDetails = await addSubscriptions(
                    currentUser.username,
                    subscriptions,
                    currentUser.token
                );
            }
            setUserDetails(updatedUserDetails);
            setUser(prevState => ({ ...updatedUserDetails, token: prevState.token }));
            notification.success({
                message: "Success!",
                description: "Your subscriptions have been updated",
            });
        }
        catch(error) {
            console.error(error)
            let errorMessage = error?.message;
            if (error?.response) {
                errorMessage = error?.response?.data?.msg
                    ? sessionExpiryMessage("update your subscriptions")
                    : error.message;
            }
            notification.error({
                message: "An error occurred updating your show subscriptions!",
                description: <Text>{errorMessage}</Text>
            });
        }
    };

    return (
        userDetails ? (
            <>
                <Helmet>
                    <title>{userDetails.username} Profile | TVGuide</title>
                </Helmet>
                <h1>{userDetails.username}</h1>
                {viewingOwnProfile && userTVGuide && (
                    <TVGuide
                        guide={userTVGuide}
                        user={userDetails}
                    />
                )}
                <div id="subscription-list-container">
                    <List
                        bordered
                        dataSource={userDetails.show_subscriptions}
                        renderItem={item => (
                            <List.Item
                                actions={viewingOwnProfile ? [
                                    <Button onClick={() => unsubscribe(item.id)}>Unsubscribe</Button>
                                ] : []}
                            >
                                <span>{item.search_item.show}</span>
                            </List.Item>
                        )}
                        header={<strong>{viewingOwnProfile ? 'Your' : `${user}'s`} Show Subscriptions</strong>}
                        className="subscription-list"
                        footer={viewingOwnProfile && (
                            <Space>
                                <Button onClick={() => toggleModal()}>Subscribe to a Show</Button>
                            </Space>
                        )}
                    />
                </div>
                <SubscriptionForm
                    showForm={showSubscriptionModal}
                    userDetails={userDetails}
                    toggleModal={toggleModal}
                    updateSubscriptionsHandle={updateSubscriptionsHandle}
                />
            </>
        )
        : !loadingUser && !userDetails ? (
            <Alert
                type="error"
                className="user-alert"
                message="Error!"
                description={`An account with the username ${user} could not be found`}
            />
        ) : (
            <Spin fullscreen />
        )
    );
};

export default ProfilePage;