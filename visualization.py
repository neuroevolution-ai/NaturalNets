import gym
import time
import cv2

env_seed = 100

env = gym.make('procgen:procgen-heist-v0', num_levels=1, start_level=env_seed, distribution_mode="memory")
obs = env.reset()


reward = 0
done = False
while not done:
    obs, rew, done, info = env.step(env.action_space.sample())

    resized = cv2.resize(obs, (500, 500))

    cv2.imshow("ProcGen Agent", resized)
    cv2.waitKey(1)

    time.sleep(0.01)

    print(rew)
    reward += rew

print(reward)
print("Finished")